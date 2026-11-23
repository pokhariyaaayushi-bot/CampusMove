FROM python:3.11-slim

WORKDIR /app

# The application is imported as the ``backend`` package, so retain the
# repository layout inside the image rather than copying backend contents to
# the image root.
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend /app/backend
COPY db /app/db
COPY frontend /app/frontend

EXPOSE 5000

ENV FLASK_ENV=development \
    HOST=0.0.0.0 \
    PORT=5000

CMD ["python", "backend/run.py"]

