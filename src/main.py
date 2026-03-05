import logging

import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

from src.users.router import router as router_user
from src.workouts.router import router as router_workout
from src.admin.admin import init_admin
from src.core.exceptions.handlers import setup_exception_handlers
from src.core.logging import configure_logging
from src.core.redis import lifespan
from src.core.cors import setup_cors
from src.core.metrics import setup_metrics
from src.core.sentry import sentry_sdk

configure_logging()

log = logging.getLogger(__name__)

app = FastAPI(
    title="Workout App",
    lifespan=lifespan,
    # docs_url=None,  # Close the documentation
)

app.mount("/api/media", StaticFiles(directory="src/media"), name="media")

# Настройка CORS
setup_cors(app)

# Настройка Prometheus
setup_metrics(app)

# Инициализируем админ-панель
init_admin(app)

setup_exception_handlers(app)

app.include_router(router_user, prefix="/api")
app.include_router(router_workout, prefix="/api")

if __name__ == "__main__":
    # uvicorn src.main:app --reload
    log.info("Application starting")
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
