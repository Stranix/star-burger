#!/usr/bin/env bash

set -e


cd /var/py_project/learn/star-burger/

echo -e "Выкачиваем изменения из репозитория..."
git pull

COMMIT=`git rev-parse --short HEAD`

echo -e "Устанавливаем библиотеки для Python..."
source ./env/bin/activate
env/bin/python -m pip install -r requirements.txt

echo -e "Устанавливаем библиотеки для Node.js..."
npm ci --include=dev

echo -e "Собираем фронтенд..."
./node_modules/.bin/parcel build bundles-src/index.js -d bundles --no-minify --public-url="./"

echo -e "Собираем статику Django..."
env/bin/python manage.py collectstatic --no-input

echo -e "Применяем миграции..."
env/bin/python manage.py migrate --no-input

echo -e "Перезапускаем сервисы Systemd..."
systemctl restart starburger.service

echo -e "Отправляем уведомление в Rollbar..."
curl -H "X-Rollbar-Access-Token: $ROLLBAR_POST_ACCESS_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "production", "revision": "'$COMMIT'"}'

echo -e "Всё готово!"

