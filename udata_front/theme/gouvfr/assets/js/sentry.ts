import * as Sentry from '@sentry/vue';
import { Integrations } from '@sentry/tracing';
import { sentry } from './config';
import { App } from 'vue';

function InitSentry(app: App) {
  if (sentry.dsn) {
    try {
      Sentry.init({
        app,
        dsn: sentry.dsn,
        environment: sentry.environment,
        integrations: [
          new Integrations.BrowserTracing({
            // Specify which origins to trace to avoid 'split' errors on undefined
            tracingOrigins: [
              'localhost',
              /^\//,
              // Match current origin
              window.location.origin,
            ].filter(Boolean),
          }),
        ],
        sampleRate: sentry.sampleRate,
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
      Sentry.setTags(sentry.tags);
    } catch (error) {
      console.warn('Failed to initialize Sentry:', error);
    }
  }
}

export default InitSentry;
