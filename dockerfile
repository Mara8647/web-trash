FROM postgres:latest

RUN mkdir /app
WORKDIR /app

COPY templates/* ./templates/
COPY scripts/* ./scripts/

EXPOSE 50
EXPOSE 5432

RUN apt update
RUN apt install -y python3 python3-pip
RUN pip install --break-system-packages flask psycopg sqlalchemy dotenv
