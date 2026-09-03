import {
  CallHandler,
  ExecutionContext,
  Injectable,
  NestInterceptor,
} from '@nestjs/common';
import { Request } from 'express';
import { Observable, tap } from 'rxjs';
import { MetricsService } from './metrics.service';

@Injectable()
export class MetricsInterceptor implements NestInterceptor {
  constructor(private readonly metrics: MetricsService) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const started = process.hrtime.bigint();
    const req = context.switchToHttp().getRequest<Request>();

    return next.handle().pipe(
      tap({
        next: () => this.record(req, started),
        error: () => this.record(req, started),
      }),
    );
  }

  private record(req: Request, started: bigint) {
    const seconds = Number(process.hrtime.bigint() - started) / 1e9;
    // Use the route template (e.g. /auth/login) to avoid high-cardinality labels
    const route = req.route?.path ?? req.baseUrl ?? 'unknown';
    const statusCode = req.res?.statusCode ?? 0;
    this.metrics.observe(req.method, route, statusCode, seconds);
  }
}
