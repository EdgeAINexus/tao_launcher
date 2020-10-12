"""Simple script to instantiate a docker handler and test it."""

import sys

from components.docker_handler.docker_handler import DockerHandler


def main(args=None):
    """Instantiate a docker handler and test interactions."""
    docker_registry = "stg.nvcr.io/nvidia/tlt-streamanalytics"
    docker_tag = "v3.0.0ga-dev"
    docker_digest = "sha256:0043e8f4221be7229919c2d2b9ba7d14a4a3a156642476440147253bb74ab5a5"
    tf_docker_handler = DockerHandler(docker_registry, docker_tag)
    mount_points = tf_docker_handler._get_mounts_from_file()
    print("{}".format(mount_points))
    print("docker instance type: {}".format(type(tf_docker_handler)))
    docker_check = tf_docker_handler.check_image_exists()
    if not docker_check:
        tf_docker_handler.pull()

    


if __name__ == "__main__":
    main(sys.argv[1:])
