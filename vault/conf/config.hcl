storage "s3" {
  region = "eu-west-3"
  bucket = "vault-data-pong42"
}

seal "awskms" {
  region     = "eu-west-3"
  kms_key_id = "fd0f6712-be3a-4de2-bae5-617e8aca3612"
}

listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = "true"  # Set to false for production with proper certs
}

telemetry {
  prometheus_retention_time = "12h"  # Metrics retention time in seconds
  disable_hostname = true  # Optional: prevents hostname from being included in metrics
}

disable_mlock = true
ui = true