FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir flask==3.1.* gunicorn==23.*
COPY app.py .
EXPOSE 8000
CMD ["gunicorn", "--preload", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]
