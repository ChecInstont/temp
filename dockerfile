FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for headless Chrome and Selenium
RUN apt-get update && \
    apt-get install -y \
    wget \
    curl \
    unzip \
    libx11-dev \
    libx264-dev \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy your application code into the container
COPY . /app/

# Set environment variables for headless Chrome (necessary for Chromium in headless mode)
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium

# Expose port 5500 (instead of 8000)
EXPOSE 5500

# Run the FastAPI application with Uvicorn on port 5500
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5500"]