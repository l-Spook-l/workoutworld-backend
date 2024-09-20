import sentry_sdk
from src.core.config import SENTRY_DNS

sentry_sdk.init(
    dsn=SENTRY_DNS,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
