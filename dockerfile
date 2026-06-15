FROM postgres:latest

RUN mkdir /app
WORKDIR /app

COPY templates/* ./templates/
COPY scripts/* ./scripts/

EXPOSE 50
EXPOSE 5432

RUN apt update
RUN apt install -y python3 python3-pip python3-venv
RUN python3 -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"
RUN pip install flask psycopg sqlalchemy

CMD ["python3", "/app/scripts/main.py"]