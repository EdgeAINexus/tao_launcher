# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
"""A docker handler to interface with the docker.

This component is responsible for:
1. Interacting with the docker registry
2. Pulling the docker from the registry
3. Instantiating a docker locally.
4. Executing the command locally.
"""

import json
import logging
import os
import requests
import sys
import subprocess

import docker

DOCKER_MOUNT_FILE = "~/.tlt_mounts.json"
DOCKER_COMMAND = "docker"
DEFAULT_DOCKER_PATH = "unix://var/run/docker.sock"

logger = logging.getLogger(__name__)


class DockerHandler(object):
    """Handler to control docker interactions."""

    def __init__(self,
                 docker_registry=None,
                 docker_tag=None,
                 docker_digest=None,
                 docker_mount_file=DOCKER_MOUNT_FILE,
                 docker_env_path=DEFAULT_DOCKER_PATH):
        """Initialize the docker handler object."""
        self._docker_client = docker.DockerClient(base_url=docker_env_path)
        self._api_client = docker.APIClient(base_url=docker_env_path)
        self._docker_registry = docker_registry
        self._docker_mount_file = os.path.expanduser(DOCKER_MOUNT_FILE)
        self._docker_tag = docker_tag
        self._docker_digest = docker_digest
        self.device_requests = docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
        self.docker_exec_command = "docker exec -it"
        self.initialized = True

    def _get_mounts_from_file(self):
        """Get the mounts from the tlt_mount.json file."""
        mount_points = []
        if not os.path.exists(self._docker_mount_file):
            print("No mount points were found in the ~/.tlt_mounts.json file.")
            return mount_points
        with open(self._docker_mount_file, 'r') as mfile:
            data = json.load(mfile)
        assert ["Mounts"] == list(data.keys()), (
            "Invalid json file. Requires Mounts key."
        )
        for mount in data["Mounts"]:
            assert 'source' in list(mount.keys()) and 'destination' in list(mount.keys()), (
                "Mounts are not formatted correctly."
            )
            if not os.path.exists(mount['source']):
                raise ValueError("Mount point source path doesn't exist. {}".format(mount['source']))
        return data["Mounts"]

    def _check_image_exists(self):
        """Check if the image exists locally."""
        image_list = self._docker_client.images.list()
        assert isinstance(image_list, list), (
            "image_list should be a list."
        )
        for image in image_list:
            image_inspection_content = self._api_client.inspect_image(image.attrs["Id"])
            if image_inspection_content["RepoDigests"]:
                image_digest = image_inspection_content["RepoDigests"][0].split("@")[1]
                if image_digest == self._docker_digest:
                    return True
        return False

    def pull(self):
        """Pull the base docker."""
        if not self.check_image_exists():
            print(
                "Container {} doesn't exist. Pulling container from the registry.".format(
                    self.docker_image
                )
            )
            try:
                self._api_client.pull(repository="stg.nvcr.io/nvidia/tlt-streamanalytics", tag="v3.0.0ga-dev")
            except requests.exceptions.HTTPError:
                raise IOError("Docker not found.")
            except docker.errors.APIError:
                raise ValueError("Docker pull failed.")
            print("Container pull complete.")

    @property
    def docker_image(self):
        """Get the docker image name."""
        if not self.initialized:
            raise ValueError("Docker instance wasn't initialized")
        return "{}:{}".format(self._docker_registry, self._docker_tag)

    def formatted_mounts(self, mountpoints_list):
        """Get formatted mounts for the docker command."""
        assert isinstance(mountpoints_list, list), (
            "Mount points provided to format must be a list"
        )
        volumes = {}
        exec_mounts = ""
        for mount in mountpoints_list:
            exec_mounts += "-v {}:{} ".format(
                mount["source"],
                mount["destination"]
            )
            volumes[mount["source"]] = {
                "bind": mount["destination"],
                "mode": "rw"
            }
        return exec_mounts, volumes

    def get_device_requests(self):
        """Create device requests for the docker."""
        device_requests = [docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])]
        return device_requests

    def start_container(self, volumes):
        """This will create a docker container."""
        self._container = self._docker_client.containers.run(
            "{}@{}".format(self._docker_registry, self._docker_digest),
            command=None,
            device_requests=self.get_device_requests(),
            tty=True,
            stderr=True,
            stdout=True,
            detach=True,
            volumes=volumes,
            remove=True
        )

    def run_container(self, task_command):
        """Instantiating an instance of the TLT docker."""
        if not self._check_image_exists():
            logger.info(
                "The required docker doesn't exist locally/the manifest has changed. "
                "Pulling a new docker.")
            self.pull()
        formatted_mounts, volumes = self.formatted_mounts(self._get_mounts_from_file())

        # Start the container if the it isn't already.
        self.start_container(volumes)

        formatted_command = "{} {} {}".format(
            self.docker_exec_command,
            self._container.id,
            task_command
        )
        print("volumes: {}".format(volumes))
        print("formatted_command: {}".format(formatted_command))
        rc = subprocess.call(formatted_command, shell=True, stdout=sys.stdout)
        return rc

    def stop_container(self):
        """Stop an instantiated container."""
        self._container.stop()
