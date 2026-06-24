FROM debian:latest

RUN mkdir /app
WORKDIR /app

COPY py_scripts/* ./py_scripts
COPY ps1_scripts/* ./ps1_scripts
COPY templates/* ./templates/
RUN touch ./py_scripts/vs_access_panel.sqlite3

EXPOSE 50170

RUN apt update
RUN apt install -y python3 python3-pip
RUN pip install --break-system-packages flask sqlalchemy transliterate bcrypt dotenv

CMD ["python3", "/app/py_scripts/main.py"]