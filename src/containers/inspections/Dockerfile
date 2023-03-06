FROM python:3.11

RUN apt update && apt install -y apt-transport-https ca-certificates dirmngr wget && \
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv E0C56BD4

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.3.2

WORKDIR /app

RUN wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
    --output-document /app/YandexCA.crt && chmod 655 /app/YandexCA.crt

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml /app

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY src /app/src

#CMD ["python", "-m", "uvicorn", "src.inspections.main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["python", "-m", "gunicorn", "src.inspections.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]