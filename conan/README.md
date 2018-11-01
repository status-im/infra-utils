# Description

This image for running the [Conan](https://conan.io/) repository server is used by the [Ansible `conan` role](https://github.com/status-im/infra-misc/tree/master/ansible/roles/conan).

# Why?

All images on Docker Hub use either uWSGI or nothing for handling the requests, this uses [Gunicorn](https://gunicorn.org/).

# Configuration

The `.conan_server` directory goes inside of `/root`:

* `/root/.conan_server/server.conf` - Server config file
* `/root/.conan_server/data` - Data directory
