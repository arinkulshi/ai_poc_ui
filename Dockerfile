# Stage 1: Build React frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/ui
COPY ui/package.json ui/package-lock.json* ./
RUN npm install
COPY ui/ ./
RUN npm run build

# Stage 2: Python backend + serve static files
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY run.py .

# Copy built frontend from stage 1
COPY --from=frontend-build /app/ui/dist ./ui/dist

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "api:create_app()"]
