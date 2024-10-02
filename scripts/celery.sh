#!/bin/bash


if [ "${1}" = "celery" ]; then
  celery --app=src.core.celery:celery_app worker -l INFO
elif [ "${1}" = "flower" ]; then
  celery --app=src.core.celery:celery_app flower
fi
