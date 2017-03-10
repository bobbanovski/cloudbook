FROM python:3.4.5-slim

# Get some custom packages
RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    gcc \
    python3-dev \
    mongodb

RUN mkdir /cloudbook
WORKDIR /cloudbook

ADD . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "manage.py", "runserver"]