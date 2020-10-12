# Transfer Learning Toolkit - Launcher

This project contains the source code to the TLT launcher interface. This launcher interface aims at providing a unified command line experience to the Transfer Learning Toolkit package.
The DNN's in TLT may be implemented in TensorFlow, Keras or PyTorch. These frameworks are difficult to maintain in the same docker. In an attempt to abstract the final customers of TLT, to handle tlt command abstracts these details away from the user.

## Installation Instructions

TLT launcher is strictly a python package. Inorder to start development, we recommend using virtualenvs to isolate your python environment.

1. Create your own python virtual environment.
2. Install the required dependancies in your virtual env.

    For developers:

    ```sh
    pip install -r depedencies/requirements-pip-dev.txt
    ```

    For users:

    ```sh
    pip install -r depedencies/requirements-pip.txt
    ```

3. Export the repo root to the python path of the virtualenv.

    ```sh
    cd $REPO_ROOT
    add2virtualenv ./
    ```

## Instructions to run the launcher.

The tlt launcher wraps contains wrappers to interact with the respective TLT docker, based on the task you wish to invoke. This wrapper is contained in the entrypoint script under `$REPO_ROOT/entrypoint/tlt.py`. For example, to run a training using detectnet_v2, the sample command would be:

```sh
python entrypoint/tlt.py detectnet_v2 -e /path/to/experiment/spec/file.prototxt -k <enc_key> -r /path/to/output/dir -n model_name
```

However, since the launcher interacts with the docker, the user is required to provide a json file containing the drives/paths that the user would like to expose to the docker. This file is expected to be present in `$HOME/.tlt_mounts.json`.

Sample contents of the mounts file would be.

```json
{
    "Mounts":[
        {
            "source": "/home/project_ivadata.cosmos369",
            "destination": "/home/project_ivadata.cosmos369"
        },
        {
            "source": "/home/IVAData2",
            "destination": "/home/IVAData2"
        },
        {
            "source": "/home/scratch.metropolis2/users/vpraveen/scratch_space/kitti-experiments",
            "destination": "/workspace/tlt-experiments"
        }
    ]
}
```
