# Stage 1: Build PostgreSQL database
FROM postgres:latest as postgres

# Set environment variables
ENV POSTGRES_USER=claims
ENV POSTGRES_PASSWORD=claims
ENV POSTGRES_DB=claimsDB

# Stage 2: Build Redis
FROM redis:6.2.3 as redis

# Stage 3: Build Python web application
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose port 1200 to the outside world
EXPOSE 1200

# Run uvicorn when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "1200", "--access-log"]
