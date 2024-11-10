from prometheus_fastapi_instrumentator import Instrumentator
from .config import METRICS_URL


def setup_metrics(app):
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app, endpoint=METRICS_URL)
