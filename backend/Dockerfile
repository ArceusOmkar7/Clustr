FROM python:3.13-slim

WORKDIR /app

RUN mkdir uploads


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
