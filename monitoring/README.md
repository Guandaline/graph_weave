# Graph Monitoring Stack

This directory contains the complete infrastructure for monitoring and observability of the `graph`, orchestrated with Docker Compose. The stack is designed to be launched with a single command, providing a powerful local solution for metrics collection, dashboard visualization, and alert management.

## Components

The monitoring stack includes the following services:

1.  **Prometheus:**
    * **Purpose:** Collects and stores time-series metrics exposed by the API at the `/internal/metrics` endpoint.
    * **Access:** `http://localhost:9090`

2.  **Grafana:**
    * **Purpose:** Enables the creation and visualization of interactive dashboards from the data collected by Prometheus.
    * **Access:** `http://localhost:3000`
    * **Default Credentials:** `admin` / `admin` (you will be prompted to change this on first login).

3.  **Alertmanager:**
    * **Purpose:** Manages alerts fired by Prometheus. It handles deduplicating, grouping, and routing notifications to configured channels.
    * **Access:** `http://localhost:9093`

## Getting Started

### Prerequisites
* Docker and Docker Compose installed on your machine.
* The `graph` must be running locally, typically on port `8000`.

### Commands (`Makefile`)

We have created shortcuts in the project's main `Makefile` to simplify stack management.

* **To start all services in the background:**
    ```bash
    mk mup
    ```
    *Alias for: `docker compose -f monitoring/docker-compose.yml up -d`*

* **To stop all services and remove volumes (full cleanup):**
    ```bash
    mk mdown
    ```
    *Alias for: `docker compose -f monitoring/docker-compose.yml down --volumes`*


## Configuration

### Slack Alerting (Required for Notifications)

To receive alert notifications, you must configure a Slack Webhook URL. This is done securely using an environment file to avoid committing secrets to version control.

**1. Create the Environment File:**

In this `monitoring/` directory, create a new file named `.env`.

**2. Add the Slack Webhook URL:**

Add your secret Webhook URL to the `.env` file like this:
```dotenv
# Secret for the Alertmanager Slack integration
SLACK_WEBHOOK_URL='https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
You can obtain this URL by creating an "Incoming Webhook" in your Slack App's configuration page.
```

**3. Ensure .env is Ignored by Git:**

Crucially, add the `monitoring/.env` file to your project's root `.gitignore` file to prevent the secret from ever being committed.

```plaintext
# .gitignore

# Local environment files
/monitoring/.env
```

The `docker-compose.yml` is already configured to read this variable from the `.env` file and inject it securely into the Alertmanager container at runtime.

### File Structure

- `docker-compose.yml`: The main file that defines and orchestrates the three services.

- `prometheus/`: Contains the Prometheus configuration.

- - `prometheus.yml`: Defines global settings, scrape targets, and points to the Alertmanager.

- -`alert.rules.yml`: Defines the alerting rules (e.g., `HighErrorRate`, `APIIsDown`).

- `alertmanager/`: Contains the Alertmanager configuration.

- - `config.yml`: Defines how alerts are processed and where they are sent. It's configured to use the `SLACK_WEBHOOK_URL` environment variable.

- `grafana/provisioning/`: Contains the automatic Grafana configuration for datasources and dashboards.