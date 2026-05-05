FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

RUN adduser --disabled-password --gecos "" appuser
USER appuser

ENV PYTHONDONTWRITEBYTECODE=1

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/version')"

CMD ["python", "main.py"]