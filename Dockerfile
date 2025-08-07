# Multi-stage Docker build for FlyerFlutter
# Production-ready configuration with frontend and backend

# ============================================
# Stage 1: Build React Frontend
# ============================================
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app/frontend

# Copy all frontend files
COPY frontend/ ./

# Remove any existing node_modules and package-lock to avoid conflicts
RUN rm -rf node_modules package-lock.json

# Install dependencies fresh in Alpine
RUN npm install

# Build the frontend application
RUN npm run build

# ============================================
# Stage 2: Setup Python Backend
# ============================================
FROM python:3.11-slim AS backend-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# ============================================
# Stage 3: Production Image
# ============================================
FROM backend-base AS production

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# ============================================
# Stage 4: Development Image (Optional)
# ============================================
FROM backend-base AS development

# Install development dependencies
RUN pip install \
    watchfiles \
    pytest-cov \
    black \
    ruff \
    mypy

# Copy all source code (including tests)
COPY . .

# Create directories and set permissions
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port with auto-reload
EXPOSE 8000

# Development command with auto-reload
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]