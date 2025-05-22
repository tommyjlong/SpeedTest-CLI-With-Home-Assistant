FROM --platform=$BUILDPLATFORM python:3.9-slim

# Install speedtest-cli and required packages
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    cron \
    && curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash \
    && apt-get install speedtest \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY speedtest-cli-2ha.py .
COPY entrypoint.sh .
COPY run-speedtest.sh .

# Make the scripts executable
RUN chmod +x entrypoint.sh run-speedtest.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
