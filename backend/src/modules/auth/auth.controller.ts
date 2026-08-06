import { Body, Controller, HttpCode, HttpStatus, Post } from '@nestjs/common';
import { AuthService } from './auth.service';
import { LoginDto } from './dto/login.dto';
import { RefreshTokenDto } from './dto/refresh-token.dto';
import { RegisterDto } from './dto/register.dto';

@Controller('auth')
export class AuthController {
  constructor(private readonly auth: AuthService) {}

  @Post('register')
  async register(@Body() payload: RegisterDto) {
    return this.auth.register(payload);
  }

  @Post('login')
  async login(@Body() payload: LoginDto) {
    return this.auth.login(payload);
  }

  @Post('refresh')
  async refresh(@Body() payload: RefreshTokenDto) {
    return this.auth.refresh(payload);
  }

  @Post('logout')
  @HttpCode(HttpStatus.NO_CONTENT)
  async logout(@Body() payload: RefreshTokenDto) {
    await this.auth.logout(payload);
  }
}
