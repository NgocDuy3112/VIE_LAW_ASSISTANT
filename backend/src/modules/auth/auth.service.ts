import { BadRequestException, Injectable, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcryptjs';
import { createHash, randomBytes } from 'crypto';
import { PrismaService } from '../../shared/prisma/prisma.service';
import { LoginDto } from './dto/login.dto';
import { RefreshTokenDto } from './dto/refresh-token.dto';
import { RegisterDto } from './dto/register.dto';

@Injectable()
export class AuthService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwt: JwtService,
    private readonly config: ConfigService,
  ) {}

  async register(payload: RegisterDto) {
    const existing = await this.prisma.user.findUnique({ where: { email: payload.email } });
    if (existing) throw new BadRequestException('Email already registered');

    const passwordHash = await bcrypt.hash(payload.password, 12);
    const user = await this.prisma.user.create({
      data: { username: payload.username, email: payload.email, passwordHash },
      select: { id: true, username: true },
    });
    return user;
  }

  async login(payload: LoginDto) {
    const user = await this.prisma.user.findUnique({ where: { email: payload.email } });
    if (!user || !(await bcrypt.compare(payload.password, user.passwordHash))) {
      throw new UnauthorizedException('Invalid credentials');
    }

    await this.prisma.refreshToken.updateMany({
      where: { userId: user.id, revoked: false },
      data: { revoked: true },
    });

    const accessToken = await this.createAccessToken(user.id);
    const refresh = this.createRefreshToken();
    await this.prisma.refreshToken.create({
      data: {
        userId: user.id,
        tokenHash: refresh.tokenHash,
        issuedAt: refresh.issuedAt,
        expiresAt: refresh.expiresAt,
      },
    });

    return { access_token: accessToken, refresh_token: refresh.token };
  }

  async refresh(payload: RefreshTokenDto) {
    const tokenHash = this.hashToken(payload.refresh_token);
    const record = await this.prisma.refreshToken.findFirst({ where: { tokenHash } });

    if (!record) throw new UnauthorizedException('Invalid token');
    if (record.expiresAt < new Date()) {
      await this.prisma.refreshToken.delete({ where: { id: record.id } });
      throw new UnauthorizedException('Refresh token expired');
    }
    if (record.revoked) {
      await this.prisma.refreshToken.updateMany({ where: { userId: record.userId }, data: { revoked: true } });
      throw new UnauthorizedException('Token reuse detected. All sessions terminated.');
    }

    const newRefresh = this.createRefreshToken();
    await this.prisma.$transaction([
      this.prisma.refreshToken.update({ where: { id: record.id }, data: { revoked: true } }),
      this.prisma.refreshToken.create({
        data: {
          userId: record.userId,
          tokenHash: newRefresh.tokenHash,
          issuedAt: newRefresh.issuedAt,
          expiresAt: newRefresh.expiresAt,
        },
      }),
    ]);

    return { access_token: await this.createAccessToken(record.userId), refresh_token: newRefresh.token };
  }

  async logout(payload: RefreshTokenDto) {
    await this.prisma.refreshToken.updateMany({
      where: { tokenHash: this.hashToken(payload.refresh_token), revoked: false },
      data: { revoked: true },
    });
  }

  private async createAccessToken(userId: string): Promise<string> {
    const expiresIn = (this.config.get<number>('ACCESS_TOKEN_EXPIRE_MINUTES') ?? 15) * 60;
    return this.jwt.signAsync({ sub: userId }, { expiresIn });
  }

  private createRefreshToken() {
    const token = randomBytes(32).toString('base64url');
    const issuedAt = new Date();
    const days = this.config.get<number>('REFRESH_TOKEN_EXPIRE_DAYS') ?? 30;
    const expiresAt = new Date(issuedAt.getTime() + days * 24 * 60 * 60 * 1000);
    return { token, tokenHash: this.hashToken(token), issuedAt, expiresAt };
  }

  private hashToken(raw: string): string {
    return createHash('sha256').update(raw).digest('hex');
  }
}
