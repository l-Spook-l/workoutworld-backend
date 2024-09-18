from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app):
    # Инициализируйте Instrumentator и подключите его к приложению
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)
