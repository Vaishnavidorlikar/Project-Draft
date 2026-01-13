terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

resource "google_storage_bucket" "function_bucket" {
  name     = "${var.project}-function-bucket"
  location = var.region
}

resource "google_cloudfunctions_function" "hello_function" {
  name        = "hello-function"
  runtime     = "python311"
  entry_point = "lambda_handler"

  source_archive_bucket = google_storage_bucket.function_bucket.name
  source_archive_object = "function-source.zip"

  trigger_http = true
  available_memory_mb = 128
}

output "cloudfunction_url" {
  value = google_cloudfunctions_function.hello_function.https_trigger_url
}
