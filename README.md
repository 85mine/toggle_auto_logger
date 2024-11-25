# Toggl Time Logger

## Overview
This is a script to automate Toggl time tracking, built to run in a Docker container.

## How to Run

1. Build the Docker image:
   ```bash
   docker-compose build
   ```

2. Start the service:
   ```bash
   docker-compose up -d
   ```

3. Check logs:
   ```bash
   docker-compose logs -f
   ```

4. Stop the service:
   ```bash
   docker-compose down
   ```

## Configuration

Set the following environment variables in the `docker-compose.yml` file:

- `EMAIL`: Your Toggl Track account email.
- `PASSWORD`: Your Toggl Track account password.
- `WORKSPACE_ID`: Your Toggl workspace ID.
- `PROJECT_ID` (optional): Toggl project ID for entries.
- `TZ`: Timezone (e.g., `Asia/Bangkok`).

## Files

- `start_messages.txt`: Custom messages for starting time entries.
- `end_messages.txt`: Custom messages for ending time entries.
- `main.py`: The Python script that handles the time logging.

## Example

Here’s an example configuration in `docker-compose.yml`:

```yaml
version: '3.8'

services:
  toggl_time_logger:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./start_messages.txt:/app/start_messages.txt
      - ./end_messages.txt:/app/end_messages.txt
      - ./main.py:/app/main.py
    environment:
      - EMAIL=your_email@example.com
      - PASSWORD=your_password
      - WORKSPACE_ID=1234567
      - TZ=Asia/Bangkok
    command: ["python", "main.py"]
    restart: always