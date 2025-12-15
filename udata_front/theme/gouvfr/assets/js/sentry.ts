import { sentry } from './config';
import { App } from 'vue';

async function InitSentry(app: App) {
  // Only load Sentry if DSN is configured
  if (!sentry.dsn) {
    return;
  }

  try {
    // Dynamic import to avoid loading Sentry when not needed
    const [Sentry, { Integrations }] = await Promise.all([
      import('@sentry/vue'),
      import('@sentry/tracing'),
    ]);

    Sentry.init({
      app,
      dsn: sentry.dsn,
      environment: sentry.environment || '',
      integrations: [
        new Integrations.BrowserTracing({
          // Specify which origins to trace to avoid 'split' errors on undefined
          tracingOrigins: [
            'localhost',
            /^\//,
            window.location?.origin,
          ].filter(Boolean),
        }),
      ],
      sampleRate: sentry.sampleRate || 0,
      release: sentry.release,
      ignoreErrors: [
        'Auth required',
        'Network Error',
        'Request aborted',
        'ResizeObserver loop limit exceeded',
        'ResizeObserver loop completed with undelivered notifications.',
      ],
      autoSessionTracking: false,
    });

    if (sentry.tags && Object.keys(sentry.tags).length > 0) {
      Sentry.setTags(sentry.tags);
    }
  } catch (error) {
    console.warn('Failed to initialize Sentry:', error);
  }
}

export default InitSentry;

