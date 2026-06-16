FROM postgres:latest

RUN mkdir /app
WORKDIR /app

COPY scripts/* ./scripts/
COPY templates/* ./templates/

EXPOSE 50

RUN apt update
RUN apt install -y python3 python3-pip
RUN pip install --break-system-packages flask sqlalchemy psycopg

CMD ["python3", "/app/scripts/main.py"]