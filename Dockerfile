FROM python:3.12.9
LABEL authors="ritter"

WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY project /app

EXPOSE 8000
EXPOSE 5432

# There can only be one CMD instruction in a Dockerfile or build stage.
# Only the last one will have an effect.
# CMD ["python", "manage.py", "migrate"]
# CMD ["python", "manage.py", "makemigrations"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]
