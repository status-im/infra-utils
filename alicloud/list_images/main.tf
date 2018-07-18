provider "alicloud" {
  access_key = "${var.alicloud_access_key}"
  secret_key = "${var.alicloud_secret_key}"
  region     = "${var.alicloud_region}"
}

data "alicloud_images" "ubuntu" {
  owners = "marketplace"
  name_regex = ".*"
}

/*
output "images" {
  value = "${data.alicloud_images.ubuntu.images.0.id}"
}
*/
