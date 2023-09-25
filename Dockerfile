FROM python:3.8

# Ustawiamy zmienną środowiskową do wyłączenia trybu buforowania dla Pythona
ENV PYTHONBUFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY .. /app/

RUN python manage.py makemigrations
RUN python manage.py migrate