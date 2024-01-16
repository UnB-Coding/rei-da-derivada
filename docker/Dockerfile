FROM python:3.11.6-alpine3.18

WORKDIR /usr/src/api

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./api/requirements.txt /usr/src/api/requirements.txt

# dependências do postres
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
RUN pip install -r /usr/src/api/requirements.txt

COPY ./api /usr/src/api/

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# código para rodar o entrypoint
ENTRYPOINT [ "/usr/src/api/config/entrypoint.sh" ]