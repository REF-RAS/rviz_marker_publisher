# RViz Marker Publisher: Installation Guide

**Robotics and Autonomous Systems Group, Research Engineering Facility, Research Infrastructure** 
**Queensland University of Technology**

![QUT REF Collection](https://badgen.net/badge/collections/QUT%20REF-RAS?icon=github) 
![ROS2 Package Category](https://badgen.net/badge/category/ROS1%20Package/purple?icon=github)
![Visualization Topic](https://badgen.net/badge/topic/Visualization/orange?icon=github)
[![License: BSD NON-AI](https://badgen.net/badge/license/BSD-3%20NON-AI?icon=github)](https://github.com/non-ai-licenses/non-ai-licenses/blob/main/NON-AI-BSD3)

----

## Installation Guide

The repository is structured as a ROS2 package as well as a Python package. 

```bash
├ rviz_marker_publisher # the root of the repository
├── config                    # store config files
├──├── demo.rviz              # a rviz2 config file specifying the topics and qos of subscriptions. 
├── docker                      # files for building and runing docker containers 
├──├── compose.yaml             # the docker compose yml file 
├──├── Dockerfile.moveit2_uv    # the dockerfile for building moveit2 image
├──├── Dockerfile.ros2_uv       # the dockerfile for building ros2 image
├──├──├ assets                  # the files used by the build process of the dockerfiles 
├── docs                        # documentation and media assets including build files for sphinx documentation
├──├── images                   # images used in the documentation
├── launch                      # ros2 launch files for this package
├── resource                        # ros2 resource folder for the marker file
├── scripts                         # tools for management of the source 
├── src                             # the package source files
├──├──  examples                       # python script examples illustrating the rviz_marker_publisher package
├──├──├── assets                       # the resource files for the examples
├──├── rviz_marker_publisher           # the python source files for the rviz_marker_publisher package
├── test                            # contains files for colcon test
├ package.xml                 # the ros2 package.xml file
├ README.md                   # the README file
├ setup.cfg                   # to specify the install script locations
├ setup.py                    # the python package setup file

``` 

### Installation as a ROS2 package

This procedure assumes a ROS2 environment is already available.  This repository also provides a ROS2 docker image for testing and development in a later section on this page.

1. Create a new ROS2 workspace or use an existing one.  In the latter, set ROS_WS to the path of the existing workspace.
```bash
export ROS2_WS=~/ros2_ws
mkdir -p ${ROS2_WS}/src
```

2. Clone this repository and save it under the `src` folder
```bash
git clone git@github.com:REF-RAS/rviz_marker_publisher.git ${ROS2_WS}/src/rviz_marker_publisher
```

3. Install the `rviz_marker_publisher` Python package.  

You are advised to use a virtual environment system such as `conda`, `uv` or `pixi` to segregate your project contexts.  Assume that conda is the choice, in your ROS2 environment, create a new conda environment.
```bash
conda create --name myproject
conda activate myproject

# Install the python package
pip install -e /workspace/ros2_ws/src/rviz_marker_publisher/
```

If the ROS2 environment is itself a virtual environment (such as a docker container), an (somewhat risky but many people are doing it) option is to install the Python package globally and directly on the operating systems. It is risky because it may interfere with the apt-based python package installation mandated by ROS2.  However, the apt-based package may often not provide the desired package nor version. 

```bash
# Install the python package globally
pip install -e /workspace/ros2_ws/src/rviz_marker_publisher/ --break-system-packages
```

The dependent python packages may also be installed by `colcon build`.  The `setup.py` file is configured to support python package installation as part of the colcon build process.

```bash
colcon build --event-handlers console_direct+
```

4. Build the ROS2 workspace with the `--symlink-install` flag.  Replace `jazzy` if the ROS2 environment is of another version.  
```bash
source /opt/ros/jazzy/setup.bash

cd ${ROS2_WS}
colcon build --symlink-install --event-handlers console_direct+ 
```
Python scripts do not require compilation.  The `symlink-install` eliminates the need to rebuild your workspace every time you change non-compiled files, saving vast amounts of development time.  It installs links in the `install` folder to the files in the `src` folder, and so updates to the Python scripts in the package are reflected in the `install` folder.

5. Install the ROS Packages (including `rviz_marker_publisher`) in the Workspace.

```bash
source install/setup.bash
```

6. Execute the test script.

```bash
ros2 run rviz_marker_publisher test_package
```
The `test_package.py` is under the `examples` folder at the top of the repository.  This and other Python scripts in the same folder are installed as control scripts by the `setup.py` file. The following tasks are executed in the test script.

- Launch a ROS2 node named `test_node`.
- Instantiate and execute an object of `rviz_marker.RvizMarkerPublisher`, which is the main class of the package.
- Publish a sphere to the default topic `/visualization_marker`.
- Publish a pointcloud to the default topic `/visualization_cloud`.
- Search for a node that has published to `/visualization_marker` (expect `test_node`)
- Search for a node that has published to `/visualization_cloud` (expect `test_node`)

The execution output should print out these tasks as listed above.


### Installation as a Python package

The `rviz_marker_publisher` Python package may be installed independently. The package is hosted with this repository on Github and it can be pip installed (or other package installers).

```bash
pip install https://github.com/REF-RAS/rviz_marker_publisher/dist/rviz_marker_publisher-0.1.0.tar.gz

```

----
## Docker Containers for ROS2 and Moveit2 Environments

The repository includes tools for building ROS2 and Moveit2 docker images and running them as docker compose services/containers.

| Docker Compose Services | Remarks                                | Execution Scripts | 
| :----------------       | :------:                               | :------:          |
| `ros2`                  | Start a container of a ROS2 environment  | `docker compose up ros2` |
| `moveit2`               | Start a container of a ROS2 environment with Moveit  | `docker compose up moveit2` |

### System Requirements of the Host Computer

- Ubuntu 20.04 or above
- Docker Engine and Docker Compose (or an equivalence such as Podman)

### Setup Procedure

1. If this repository is not already downloaded onto the host computer at `~/ros2_ws/src/rviz_marker_publish`,  execute the following commands.

```bash
export ROS2_WS=~/ros2_ws
mkdir -p ${ROS2_WS}/src

git clone git@github.com:REF-RAS/rviz_marker_publisher.git ${ROS2_WS}/src/rviz_marker_publisher
```

2. Launch the docker compose service `ros2` after change directory to the `docker` folder.

```bash
cd ${ROS2_WS}/docker
docker compose up ros2 -d
```
When launching the service for the first time, docker will pull the image `ghcr.io/ref-ras/ros2` from the Github Container Registry (GHCR) that this repository has built. This may take a few minutes.

The `up` command will launch a container of the `ros2` image and mount a few folders of the host computer to the container.

- `/tmp/.X11-unix` is mapped to `/tmp/.X11-unix` in the container
- `/etc/timezone` is mapped to `/etc/timezone` in the container
- `/etc/localtime` is mapped to `/etc/localtime` in the containter 
- `~/ros2_ws/src/rviz_marker_publisher` is mapped to `/workspace/ros2_ws/src/rviz_marker_publisher` in the container

The last item maps the local clone of this repository to a folder in the container, from which the `rviz_marker_publisher` can be installed in the container. Any change to the repository in the container (such as adding a new script) is made persistence even after the container is destroyed.

Refer to the file `docker/compose.yml` under `ros2` and then `volumes` for modifying the above mappings (such as mounting another folder for development work).

3. Ensure that the container is up and running.  Expect to see a container of the image `ghcr.io/ref-ras/ros2` is up and running.

```bash
docker container ls --all
```

4. Bring up a bash shell of the container.

```bash
docker compose exec ros2 bash
```

5. Use the shell prompt to install `rviz_marker_publisher` in the container and build the ROS2 workspace.

```bash
cd /workspace/ros2_ws/
colcon build --event-handlers console_direct+
```

6. Test the installation using the test script `test_package`.

```bash
source install/setup.bash
ros2 run rviz_marker_publisher test_package
```

### The `ros2` container 

The key characteristics of the `ros2` docker container
- Ubuntu 22.04
- Python 3.12.3
- ROS2 Jazzy
- Default username: `ubuntu` (can be updated in the docker compose.yaml file)
- Default goupname: `ubuntu` (can be updated in the docker compose.yaml file)

The default home folder of the user is at `/workspace` in the container. The folder structure is shown below.

```bash
── workspace
├── ros2_ws                           # the ROS2 workspace
├──├── src                            # the src folder of the ROS2 workspace
├──├──├── rviz_marker_publisher       # the local clone repository is mounted here 
├──├── build                        # the build folder (created by the colcon build process)
├──├── install                      # the install folder (created by the colcon build process)
├──├──├── setup.bash                # the script to configure the environment for running the scripts of rviz_marker_publisher and other packages in the workspace
├──├── log                          # the log folder (created by the colcon build process)
```

### Configuration of the Container

Edit the `compose.yml` file to configure several aspects of the container.  The following table lists the parameters under the `build/args` branch.

| Enviroment Variables | Remarks     | Default Value | 
| :--------    | :------:         | :------:          |
| `USER`       | The login user name of the container  | `ubuntu` |
| `HOST_UID`       | The UID of the login user  | 1000 |
| `HOST_GID`       | The GID (group id) of the login user | 1000 |
| `HOME`       | The home folder of the user | `/workspace` |
| `ROS_DISTRO`       | The name of the ROS2 distribution | `jazzy` |

To ensure that the new files created in the container under the mounted folder from the host computer are owned by the user on the host computer, 
the `HOST_UID` and `HOST_GID` of the container user and the host computer user should be the same.  Use the command `id` to find out the UID and GID of the user 
of two environment.

The default `HOME` folder of the container is `/workspace`, where the ROS2 workspace and its packages should be stored.

Note that an docker image build is required for any change to these parameters to take effect.
```bash
cd ${ROS2_WS}/src/rviz_marker_publisher/docker
# first bring down the running container
docker compose down
# re-build the image locally
docker compose build ros
```
Then bring up a new container of the image after the build is completed.

```bash
docker compose up ros2 -d
```

----
### Developer

Dr Andrew Lui, Senior Research Engineer <br />
Robotics and Autonomous Systems, Research Engineering Facility <br />
Research Infrastructure <br />
Queensland University of Technology <br />

Latest update: August 2026

