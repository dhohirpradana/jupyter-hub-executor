FROM python:3.8-slim-buster

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Add SSL certificate and key files
# COPY cert.pem /app
# COPY key.pem /app

# ENV FLASK_RUN_HOST=0.0.0.0

ENV JUPYTERHUB_URL=http://10.10.65.65:30822
ENV JUPYTERHUB_WS=ws://10.10.65.65:30822
ENV JUPYTERHUB_TOKEN=f4da8b468a0a4013a49a698106feb98d
ENV SOLR_URL=http://10.10.65.1:8983/solr
ENV ELASTIC_URL=http://10.10.65.65:30997

# Run the Flask application
CMD ["flask", "run"]