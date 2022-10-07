variable "GOOGLE_CREDENTIALS" {
  type = string
}
variable "PROJECT_ID" {
  type = string
}

variable "REPO_NAME" {
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

resource "google_service_account" "github-actions" {
  project      = "${var.PROJECT_ID}"
  account_id   = "github-actions"
  display_name = "A service account for GitHub Actions"
}

resource "google_project_service" "project" {
  project = "${var.PROJECT_ID}"
  service = "iamcredentials.googleapis.com"
}

resource "google_iam_workload_identity_pool" "github-actions" {
  provider                  = google-beta
  project                   = "${var.PROJECT_ID}"
  workload_identity_pool_id = "gh-oidc-pool"
  display_name              = "gh-oidc-pool"
  description               = "Workload Identity Pool for GitHub Actions"
}

resource "google_iam_workload_identity_pool_provider" "github-actions" {
  provider                           = google-beta
  project                            = "${var.PROJECT_ID}"
  workload_identity_pool_id          = google_iam_workload_identity_pool.github-actions.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-actions"
  display_name                       = "github-actions"
  description                        = "OIDC identity pool provider for GitHub Actions"
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "admin-account-iam" {
  service_account_id = google_service_account.github-actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github-actions.name}/attribute.repository/${var.REPO_NAME}"
}