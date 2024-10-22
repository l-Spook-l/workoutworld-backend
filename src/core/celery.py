from celery import Celery

# Настройка Celery (используем Redis как брокер и бэкэнд)
celery_app = Celery(
    "tasks",
    broker="redis://redis_app:6379/0",  # URL вашего Redis
    backend="redis://redis_app:6379/0"  # URL для хранения результатов
)

celery_app.conf.update(
    result_expires=3600,
)

# Автодетектирование задач в нескольких папках
celery_app.autodiscover_tasks([
    "src.users.tasks",
    "src.workouts.tasks",
])
