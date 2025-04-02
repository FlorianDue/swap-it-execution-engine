# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

from python_on_whales import DockerClient
import threading
class DockerComposeEnvironment:
    def __init__(self, services):
        self.services = services
        self.docker = None
        self.default_docker_compose_files = ["./tests/test_helpers/util/docker-compose.yaml"]

    def start_docker_compose(self, compose_files):
        #print("start")
        compose_files = self.default_docker_compose_files if compose_files is None else compose_files
        self.docker = DockerClient(compose_files=compose_files)
        self.docker.compose.up(services=self.services, pull="missing", quiet=True)

    def run_docker_compose(self, compose_files = None):
        thread = threading.Thread(target=self.start_docker_compose, args=(compose_files,))
        thread.start()

    def stop_docker_compose(self):
        self.docker.compose.down(self.services)
        #print("stop")