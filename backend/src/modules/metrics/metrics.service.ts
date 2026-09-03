import { Injectable } from '@nestjs/common';
import { collectDefaultMetrics, Histogram, Registry } from 'prom-client';

@Injectable()
export class MetricsService {
  readonly registry = new Registry();

  private readonly httpDuration: Histogram<string>;

  constructor() {
    collectDefaultMetrics({ register: this.registry });

    this.httpDuration = new Histogram({
      name: 'http_request_duration_seconds',
      help: 'HTTP request duration in seconds',
      labelNames: ['method', 'route', 'status_code'] as const,
      buckets: [0.01, 0.05, 0.1, 0.3, 0.5, 1, 3, 5, 10],
      registers: [this.registry],
    });
  }

  observe(method: string, route: string, statusCode: number, seconds: number) {
    this.httpDuration
      .labels(method, route, String(statusCode))
      .observe(seconds);
  }

  async metrics(): Promise<string> {
    return this.registry.metrics();
  }
}
