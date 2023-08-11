#!/usr/bin/env bash

set -e


cd /var/py_project/learn/star-burger/

echo -e "Останавливаем текущие контейнеры проекта..."
docker compose -f docker-compose.prod.yml down

echo -e "Выкачиваем изменения из репозитория..."
git pull

COMMIT=`git rev-parse --short HEAD`
LOCAL_USERNAME=$(whoaim)

echo -e "Пересобираем контейнеры и запускаем..."
docker compose -f docker-compose.prod.yml up -d --build 

echo -e "Собираем статику Django..."
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear  

echo -e "Отправляем уведомление в Rollbar..."
curl -H "X-Rollbar-Access-Token: $ROLLBAR_POST_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "production", "revision": "'$COMMIT'", "local_username": "'$LOCAL_USERNAME'"}'

echo -e "Всё готово!"

