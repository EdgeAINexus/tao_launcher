# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.

"""Simple script to launch detectnet commands."""

import logging
import os
import sys

from components.docker_handler.docker_handler import DockerHandler

supported_tasks = ["detectnet_v2", "faster_rcnn"]
docker_mapping = {
    "detectnet_v2": {
        "docker_registry": "stg.nvcr.io/nvidia/tlt-streamanalytics",
        "docker_tag": "v3.0.0ga-dev",
        "docker_digest": "sha256:0043e8f4221be7229919c2d2b9ba7d14a4a3a156642476440147253bb74ab5a5"
    },
    "faster_rcnn": {
        "docker_registry": "stg.nvcr.io/nvidia/tlt-streamanalytics",
        "docker_tag": "v3.0.0ga-dev",
        "docker_digest": "sha256:0043e8f4221be7229919c2d2b9ba7d14a4a3a156642476440147253bb74ab5a5"
    },
}

logger = logging.getLogger(__name__)


def main(args=None):
    """Simple function to run main."""
    # TODO: @vpraveen: Logger config has been hardcoded. Do remember to fix this.
    verbosity = "INFO"
    # Configuring the logger.
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        level=verbosity
    )

    # Get task from the command line arguments.
    task = args[0]
    assert task in supported_tasks, (
        "Task asked is not supported in this version of TLT. Please run tlt init or tlt update"
        "if you wish to look for latest tasks supported.\nTask asked: {}\nSupported tasks: {}".format(
            task, supported_tasks
        )
    )
    docker_details = docker_mapping[task]
    tf_docker_handler = DockerHandler(
        docker_registry=docker_details["docker_registry"],
        docker_tag=docker_details["docker_tag"],
        docker_digest=docker_details["docker_digest"]
    )
    command = " ".join(args)
    try:
        _ = tf_docker_handler.run_container(command)
    finally:
        tf_docker_handler.stop_container()


if __name__ == "__main__":
    main(sys.argv[1:])
