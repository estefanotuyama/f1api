# dockerfile for backend deployment

FROM python:3.11-slim

WORKDIR /code

COPY . ./backend/

RUN pip install --no-cache-dir -r backend/requirements.txt

ENV PYTHONPATH=/code

EXPOSE 8080
