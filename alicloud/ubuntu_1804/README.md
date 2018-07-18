# Description

This is for creating an Ubuntu 18.04 image for use in Alibaba Cloud.
As it stands today - 19/08/2018 - Alibaba has no official images for 18.04 so we have to make due.

# Usage

Just run:
```
packer build main.json
```
You might have to update the `source_image` if it's been a while.
