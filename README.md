# CALENDAR
Calendar is a service for scheduling meetings, events and cases.

## Stack
•	Python 3.11
•	Django 4.0.1
•	PostgreSQL 15.0

## Install

Сlone the repo 
```sh
git clone https://github.com/holistr/calendar/tree/lesson36/todolist
```

Install the dependencies

```sh
pip install requirements.txt
```

Rooll up migrations

```sh
python todolist/manage.py migrate
```
Create superuser

```sh
python todolist/manage.py createsuperuser
```
Start DB

```sh
docker-compose up -d
```
Run up

```sh
python todolist/manage.py runserver
```
