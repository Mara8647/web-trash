FROM python:3.14-slim

RUN mkdir /app
WORKDIR /app

COPY . .
RUN touch /app/vs_access_panel.sqlite3

RUN pip install -r requirements.txt

CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "main:app"]