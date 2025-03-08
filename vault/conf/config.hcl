storage "file" {
  path = "/vault/data"
}

listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = "true"  # Set to false for production with proper certs
}

telemetry {
  prometheus_retention_time = "12h"  # Metrics retention time in seconds
  disable_hostname = true  # Optional: prevents hostname from being included in metrics
}

unauthenticated_metrics_access = true
disable_mlock = true
ui = true