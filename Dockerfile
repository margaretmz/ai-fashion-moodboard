FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends nginx ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY mb_app.py ./
COPY prompt_templates ./prompt_templates
COPY real_time_patterns.py ./
COPY ref_app.py ./

COPY --from=frontend-build /app/frontend/dist /var/www/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/start.sh /app/docker/start.sh
RUN chmod +x /app/docker/start.sh

EXPOSE 7860

CMD ["/app/docker/start.sh"]

