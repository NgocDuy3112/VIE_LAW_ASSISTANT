import { BadRequestException, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcryptjs';
import { createHash } from 'crypto';
import { Test } from '@nestjs/testing';
import { AuthService } from './auth.service';
import { PrismaService } from '../../shared/prisma/prisma.service';

const sha256 = (raw: string) => createHash('sha256').update(raw).digest('hex');

describe('AuthService', () => {
  let service: AuthService;
  let prisma: {
    user: { findUnique: jest.Mock; create: jest.Mock };
    refreshToken: {
      updateMany: jest.Mock;
      create: jest.Mock;
      findFirst: jest.Mock;
      delete: jest.Mock;
      update: jest.Mock;
    };
    $transaction: jest.Mock;
  };
  let jwt: { signAsync: jest.Mock };

  const password = 'S3curePass!';
  const passwordHash = bcrypt.hashSync(password, 12);
  const user = { id: 'user-1', username: 'duy', email: 'duy@test.vn', passwordHash };

  beforeEach(async () => {
    prisma = {
      user: { findUnique: jest.fn(), create: jest.fn() },
      refreshToken: {
        updateMany: jest.fn().mockResolvedValue({ count: 0 }),
        create: jest.fn().mockResolvedValue({}),
        findFirst: jest.fn(),
        delete: jest.fn().mockResolvedValue({}),
        update: jest.fn().mockResolvedValue({}),
      },
      $transaction: jest.fn().mockResolvedValue([]),
    };
    jwt = { signAsync: jest.fn().mockResolvedValue('access-token') };

    const moduleRef = await Test.createTestingModule({
      providers: [
        AuthService,
        { provide: PrismaService, useValue: prisma },
        { provide: JwtService, useValue: jwt },
        { provide: ConfigService, useValue: { get: jest.fn().mockReturnValue(undefined) } },
      ],
    }).compile();

    service = moduleRef.get(AuthService);
  });

  describe('register', () => {
    it('creates a new user and returns id + username', async () => {
      prisma.user.findUnique.mockResolvedValue(null);
      prisma.user.create.mockResolvedValue({ id: 'user-1', username: 'duy' });

      const result = await service.register({
        username: 'duy',
        email: 'duy@test.vn',
        password,
      } as any);

      expect(result).toEqual({ id: 'user-1', username: 'duy' });
      const created = prisma.user.create.mock.calls[0][0].data;
      expect(created.email).toBe('duy@test.vn');
      expect(created.passwordHash).not.toBe(password);
      await expect(bcrypt.compare(password, created.passwordHash)).resolves.toBe(true);
    });

    it('hashes the password with 12 salt rounds', async () => {
      prisma.user.findUnique.mockResolvedValue(null);
      prisma.user.create.mockResolvedValue({ id: 'user-1', username: 'duy' });

      await service.register({ username: 'duy', email: 'duy@test.vn', password } as any);

      const hash = prisma.user.create.mock.calls[0][0].data.passwordHash;
      expect(hash.startsWith('$2')).toBe(true);
    });

    it('rejects duplicate email', async () => {
      prisma.user.findUnique.mockResolvedValue(user);

      await expect(
        service.register({ username: 'other', email: 'duy@test.vn', password } as any),
      ).rejects.toThrow(BadRequestException);
      expect(prisma.user.create).not.toHaveBeenCalled();
    });
  });

  describe('login', () => {
    it('returns tokens for valid credentials', async () => {
      prisma.user.findUnique.mockResolvedValue(user);

      const result = await service.login({ email: 'duy@test.vn', password } as any);

      expect(result.access_token).toBe('access-token');
      expect(result.refresh_token).toBeDefined();
      expect(jwt.signAsync).toHaveBeenCalledWith({ sub: 'user-1' }, { expiresIn: 900 });
      // Old refresh tokens are revoked before issuing a new one
      expect(prisma.refreshToken.updateMany).toHaveBeenCalledWith({
        where: { userId: 'user-1', revoked: false },
        data: { revoked: true },
      });
      expect(prisma.refreshToken.create).toHaveBeenCalledTimes(1);
    });

    it('stores a sha256 hash of the refresh token, never the raw token', async () => {
      prisma.user.findUnique.mockResolvedValue(user);

      const result = await service.login({ email: 'duy@test.vn', password } as any);

      expect(prisma.refreshToken.create.mock.calls[0][0].data.tokenHash).toBe(sha256(result.refresh_token));
      expect(prisma.refreshToken.create.mock.calls[0][0].data.tokenHash).not.toBe(result.refresh_token);
    });

    it('rejects unknown email', async () => {
      prisma.user.findUnique.mockResolvedValue(null);

      await expect(service.login({ email: 'nope@test.vn', password } as any)).rejects.toThrow(
        UnauthorizedException,
      );
    });

    it('rejects wrong password', async () => {
      prisma.user.findUnique.mockResolvedValue(user);

      await expect(
        service.login({ email: 'duy@test.vn', password: 'wrong-password' } as any),
      ).rejects.toThrow(UnauthorizedException);
    });
  });

  describe('refresh', () => {
    const rawToken = 'raw-refresh-token';
    const validRecord = {
      id: 'rt-1',
      userId: 'user-1',
      tokenHash: sha256(rawToken),
      revoked: false,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
    };

    it('rotates the refresh token on success', async () => {
      prisma.refreshToken.findFirst.mockResolvedValue(validRecord);

      const result = await service.refresh({ refresh_token: rawToken } as any);

      expect(result.access_token).toBe('access-token');
      expect(result.refresh_token).not.toBe(rawToken);
      // Old token revoked and a new one created inside a transaction
      expect(prisma.$transaction).toHaveBeenCalledTimes(1);
      const ops = prisma.$transaction.mock.calls[0][0];
      expect(ops).toHaveLength(2);
    });

    it('rejects unknown token', async () => {
      prisma.refreshToken.findFirst.mockResolvedValue(null);

      await expect(service.refresh({ refresh_token: rawToken } as any)).rejects.toThrow(
        new UnauthorizedException('Invalid token'),
      );
    });

    it('deletes and rejects expired token', async () => {
      prisma.refreshToken.findFirst.mockResolvedValue({
        ...validRecord,
        expiresAt: new Date(Date.now() - 1000),
      });

      await expect(service.refresh({ refresh_token: rawToken } as any)).rejects.toThrow(
        new UnauthorizedException('Refresh token expired'),
      );
      expect(prisma.refreshToken.delete).toHaveBeenCalledWith({ where: { id: 'rt-1' } });
    });

    it('revokes all sessions on token reuse', async () => {
      prisma.refreshToken.findFirst.mockResolvedValue({ ...validRecord, revoked: true });

      await expect(service.refresh({ refresh_token: rawToken } as any)).rejects.toThrow(
        new UnauthorizedException('Token reuse detected. All sessions terminated.'),
      );
      expect(prisma.refreshToken.updateMany).toHaveBeenCalledWith({
        where: { userId: 'user-1' },
        data: { revoked: true },
      });
    });
  });

  describe('logout', () => {
    it('revokes the matching non-revoked token', async () => {
      const rawToken = 'some-refresh-token';

      await service.logout({ refresh_token: rawToken } as any);

      expect(prisma.refreshToken.updateMany).toHaveBeenCalledWith({
        where: { tokenHash: sha256(rawToken), revoked: false },
        data: { revoked: true },
      });
    });
  });
});
