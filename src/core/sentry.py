import sentry_sdk


sentry_sdk.init(
    dsn="https://c12ef8b4f545287909daffa3b97d66f6@o4507941131583488.ingest.de.sentry.io/4507941149343824",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
