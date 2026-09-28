FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY database.py models.py main.py ./

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
