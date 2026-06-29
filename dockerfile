FROM debian:latest

RUN mkdir /app
WORKDIR /app

RUN mkdir -p ./py_scripts ./ps1_scripts ./templates ./templates/partials ./static
RUN openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365
COPY py_scripts/* ./py_scripts
COPY main.py ./
COPY ps1_scripts/* ./ps1_scripts
COPY static/* ./static/
COPY templates/* ./templates/
COPY templates/partials/* ./templates/partials
RUN touch /app/vs_access_panel.sqlite3

EXPOSE 50170

RUN apt update
RUN apt install -y python3 python3-pip
RUN pip install --break-system-packages flask sqlalchemy transliterate bcrypt dotenv

CMD ["python3", "/app/main.py"]