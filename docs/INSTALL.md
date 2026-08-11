# RViz Marker Publisher: Installation Guide

**Robotics and Autonomous Systems Group, Research Engineering Facility, Research Infrastructure** 
**Queensland University of Technology**

![QUT REF Collection](https://badgen.net/badge/collections/QUT%20REF-RAS?icon=github) 
![ROS2 Package Category](https://badgen.net/badge/category/ROS1%20Package/purple?icon=github)
![Visualization Topic](https://badgen.net/badge/topic/Visualization/orange?icon=github)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

---

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
├──├──├ assets                   # the files used by the build process of the dockerfiles 
├── docs                        # documentation and media assets
├── examples                            # python script examples illustrating the rviz_marker_publisher package
├──├── assets                           # the resource files for the examples
├── launch                      # ros2 launch files for this package
├── resource                        # ros2 resource folder for the marker file
├── rviz_marker                 # the python source files for the rviz_marker_publisher package
├ package.xml                 # the ros2 package.xml file
├ README.md                   # the README file
├ setup.cfg                 # to specify the install script locations
├ setup.py                  # the python package setup file

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

The dependent python packages may also be installed by `colcon build`.  The `setup.py` file is designed to support python package installation as part of the build process.

```bash
colcon build
```




