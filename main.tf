variable "GOOGLE_CREDENTIALS" {
  type = string
}
variable "PROJECT_ID" {
  type = string
}

# As of October 2022, only e2-micro instances in Oregon (us-west1), Iowa (us-central1),
# and South Carolina (us-east1) are eligible for the Google Cloud Platform's free tier.
# ref: https://cloud.google.com/free/docs/free-cloud-features?hl=ja#compute
#
# If you want to build the server for free, please do not change region or zone
# to another value (e.g. asia-northeast1).
provider "google" {
  credentials = "${var.GOOGLE_CREDENTIALS}"
  project     = "${var.PROJECT_ID}"
  region  = "us-central1"
  zone    = "us-central1-c"
}

resource "google_compute_instance" "vm_instance" {
  name         = "bot-instance"
  machine_type = "e2-micro"
  tags = ["bot-instance"]

  boot_disk {
    initialize_params {
      size  = 10
      type  = "pd-standard"
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral IP
    }
  }
}

#resource "google_compute_network" "vpc_network" {
#  name                    = "bot-network"
#  auto_create_subnetworks = "true"
#}

resource "google_compute_firewall" "default" {
 name    = "bot-firewall"
 network = "default"

 allow {
   protocol = "icmp"
 }

 allow {
   protocol = "tcp"
   ports    = ["80", "22"]
 }

 source_ranges = ["0.0.0.0/0"]
 target_tags = ["bot-instance"]
}

resource "google_iam_workload_identity_pool" "bot" {
  workload_identity_pool_id = "bot-pool"
}