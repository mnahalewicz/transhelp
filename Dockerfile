FROM python:3.8.10
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y sox libsox-fmt-mp3 nginx
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY transhelp /code/
RUN python /code/manage.py makemigrations trans
RUN python /code/manage.py migrate
