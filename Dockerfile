# Stage 1: Base build stage
FROM python:3.13.5-slim-bookworm

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip  
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN useradd -ms /bin/bash tammie 
USER tammie


CMD ["flask", "--app", "app/server", "run", "--host=0.0.0.0", "-p", "8000", "--debug"]