FROM python:3.11.4-alpine3.18

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV APP_HOME=/opt/starburger/app

RUN mkdir -p $APP_HOME

WORKDIR $APP_HOME
COPY backend/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY backend/. .

CMD ["gunicorn", "star_burger.wsgi:application", "--bind 0.0.0.0:8000", "--workers 3"]

EXPOSE 8000
VOLUME ["/media"]
