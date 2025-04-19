# Environment Variables Configuration

This directory contains environment variable configuration files for various services in the project.

## Structure

- `root/` - Root level environment variables used by docker-compose and makefile
- `front/` - Frontend service environment variables
- `back/` - Backend service environment variables
- `db/` - Database service environment variables
- `waf/` - WAF/Reverse Proxy environment variables
- `vault/` - Vault service environment variables
- `prometheus/` - Prometheus monitoring environment variables
- `db-exporter/` - Database exporter environment variables
- `grafana/` - Grafana dashboard environment variables

## Usage

The `.env` files in this directory should not be committed to git. They contain sensitive information such as API keys, passwords, and other credentials.

When cloning this repository, you'll need to create your own `.env` files based on the examples or documentation provided for each service.

## Environment Types

The project supports different environment configurations:
- Development: `.env.development` files
- Production: `.env.production` files

The environment is specified through the `ENVIRONMENT` variable in the makefile. 