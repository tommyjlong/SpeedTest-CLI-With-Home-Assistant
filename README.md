# SpeedTest To Home Assistant

This project provides a way for Home Assistant to run the official `speedtest.net` binary using either Docker Compose or manual installation. It integrates with Home Assistant to provide accurate speed test measurements using the official Speedtest CLI.

## Table of Contents
- [Quick Start with Docker Compose](#quick-start-with-docker-compose)
- [Manual Installation](#manual-installation)
- [Home Assistant Configuration](#home-assistant-configuration)
- [Testing and Debugging](#testing-and-debugging)

## Quick Start with Docker Compose

The easiest way to get started is using Docker Compose. Make sure you have Docker and Docker Compose installed on your system.

### Steps:
1. Use the following `docker-compose.yml`:

```yaml
version: '3.8'

services:
  speedtest:
    image: ghcr.io/tommyjlong/speedtest-cli-with-home-assistant:master
    container_name: speedtest-ha
    environment:
      - HA_SERVER=http://localhost:8123 # Replace with your Home Assistant URL
      - HA_AUTH_KEY=my-token # Replace with your Home Assistant Long-Lived Access Token
      - CRON_SCHEDULE=${CRON_SCHEDULE:-"*/60 * * * *"} # Default to every hour
      - SENSOR_DOWNLOAD=${SENSOR_DOWNLOAD} # will be to sensor.speedtest_${SENSOR_DOWNLOAD}
      - SENSOR_UPLOAD=${SENSOR_UPLOAD} # will be to sensor.speedtest_${SENSOR_UPLOAD}
      - SENSOR_PING=${SENSOR_PING} # will be to sensor.speedtest_${SENSOR_PING}
      # - SPEEDTEST_SERVER_ID=
      # - INCLUDE_LTS=
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro  # Sync container time with host
```

2. Start the container with:

```bash
docker compose up -d
```

## Manual Installation

If you prefer to set up manually, follow these steps:

1. **Download the Speedtest CLI Binary**:
   - Visit the [Speedtest CLI website](https://www.speedtest.net/apps/cli) and download the appropriate binary for your system.
   - Place the binary in your desired directory and ensure it is executable.

2. **Prepare the Python Script**:
   - Copy the `speedtest-cli-2ha.py` file to your desired directory.
   - Edit the file to configure the environment variables (e.g., `HA_SERVER`, `HA_AUTH_KEY`).

3. **Accept the Speedtest CLI EULA**:
   - Run the binary manually to accept the EULA, or modify the Python script to include the `--accept-license` and `--accept-gdpr` flags.

4. **Run the Script**:
   - Execute the Python script to test the integration.

## Home Assistant Configuration

1. **Setup the Speedtest Integration**:
   - Install the native [Speedtest.net integration](https://www.home-assistant.io/integrations/speedtestdotnet/) in Home Assistant.
   - Configure it to run in manual mode by disabling "Enable polling for updates" in the integration settings.

2. **Generate a Long-Lived Access Token**:
   - Go to your Home Assistant user profile and create a "Long-Lived Access Token". Copy the token and use it in the Python script.

## Testing and Debugging

1. **Debugging**:
   - Set `DEBUG=1` and `CONSOLE=1` in the Python script to enable detailed logging.
   - Run the script manually to verify the output and identify any issues.

## Notes
- Ensure the Speedtest CLI binary is accessible and executable by the script.
- Use the logs to troubleshoot any issues with the integration or script execution.
