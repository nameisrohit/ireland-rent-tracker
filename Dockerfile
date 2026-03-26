# Dockerfile
# ============================================================
# Ireland Rent Tracker — Docker Container
#
# What is a base image?
# We start FROM an existing image that already has Python.
# Like inheriting a fully set up computer.
# python:3.12-slim = Python 3.12 on minimal Linux
# slim = smaller size, faster to download
# ============================================================

FROM python:3.12-slim

# ── Set working directory ──────────────────────────────────
# All commands run from this folder inside the container
# Like cd /app
WORKDIR /app

# ── Install system dependencies ────────────────────────────
# Some Python libraries need system packages
# We install them first before Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Copy requirements first ────────────────────────────────
# Why copy requirements before code?
# Docker caches each step. If requirements haven't changed,
# Docker skips reinstalling them — much faster builds.
# This is called layer caching — important Docker pattern.
COPY requirements.txt .

# ── Install Python dependencies ────────────────────────────
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project code ──────────────────────────────────────
# Now copy everything else
# .dockerignore will exclude files we don't need
COPY . .

# ── Expose port ────────────────────────────────────────────
# Streamlit runs on port 8501
# EXPOSE tells Docker this container uses this port
EXPOSE 8501

# ── Health check ───────────────────────────────────────────
# Docker periodically checks if the container is healthy
# If it fails 3 times Docker knows something is wrong
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health \
    || exit 1

# ── Start command ──────────────────────────────────────────
# This runs when the container starts
# --server.address=0.0.0.0 = accept connections from outside
# --server.port=8501 = run on this port
CMD ["streamlit", "run", "dashboard/app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true"]