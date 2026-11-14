FROM docker.io/library/python:3.13-slim

WORKDIR /app

# Install OS updates and Python packages, then remove pip since the app doesn't need it.
COPY requirements.txt .
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir -r requirements.txt \
 && pip uninstall -y pip

COPY main.py .

# Run as a normal user. /data is where the database volume is mounted.
RUN useradd --uid 1000 app && mkdir /data && chown app /data
USER app

ENV DB_PATH=/data/app.db
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
