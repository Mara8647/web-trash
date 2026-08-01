FROM python:3.14-slim

RUN mkdir /app
WORKDIR /app

# RUN mkdir -p ./py_scripts ./ps1_scripts ./templates ./templates/partials ./static
# COPY cert.pem ./
# COPY key.pem ./
# COPY py_scripts/* ./py_scripts
# COPY main.py ./
# COPY ps1_scripts/* ./ps1_scripts
# COPY static/* ./static/
# COPY templates/* ./templates/
# COPY templates/partials/* ./templates/partials
COPY . .
RUN touch /app/vs_access_panel.sqlite3

# COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "main:app"]