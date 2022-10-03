# GCPのGoogle Compute Engine無料枠は2022年10月現在
# オレゴン(us-west1), アイオワ(us-central1), サウスカロライナ(us-east1)
# におけるe2-microインスタンスのみが対象です。
# ref: https://cloud.google.com/free/docs/free-cloud-features?hl=ja#compute
#
# 無料枠を使用したい方は、近いロケーションにサーバを設置したいからといって
# regionやzoneをasia-northeast1に変更しないでください。
provider "google" {
  project = "trade-bot"
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