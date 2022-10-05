variable "GOOGLE_CREDENTIALS" {}
variable "PROJECT_ID" {}

# As of October 2022, only e2-micro instances in Oregon (us-west1), Iowa (us-central1),
# and South Carolina (us-east1) are eligible for the Google Cloud Platform's free tier.
# ref: https://cloud.google.com/free/docs/free-cloud-features?hl=ja#compute
#
# If you want to build the server for free, please do not change region or zone
# to another value (e.g. asia-northeast1).
provider "google" {
  credentials = var.GOOGLE_CREDENTIALS
  project     = var.PROJECT_ID
  region  = "us-central1"
  zone    = "us-central1-c"
}

resource "google_compute_instance" "vm_instance" {
  name         = "bot-instance"
  machine_type = "e2-micro"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.self_link
    access_config {
    }
  }
}

resource "google_compute_network" "vpc_network" {
  name                    = "bot-network"
  auto_create_subnetworks = "true"
}