FROM python:3.12-slim

WORKDIR /app

# Instalăm dependințele
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Adăugăm codul
COPY . .

CMD ["python", "main.py"]
