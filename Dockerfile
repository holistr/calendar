FROM python:3.10-slim

ENV PYTHONBUFFERED 1

WORKDIR /app/todolist

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD python todolist/manage.py runserver 0.0.0.0:8000
