# RViz Marker Tools for ROS2

**Robotics and Autonomous Systems Group, Research Engineering Facility, Research Infrastructure** 
**Queensland University of Technology**

![QUT REF Collection](https://badgen.net/badge/collections/QUT%20REF-RAS?icon=github) 
![ROS2 Package Category](https://badgen.net/badge/category/ROS1%20Package/purple?icon=github)
![Visualization Topic](https://badgen.net/badge/topic/Visualization/orange?icon=github)
[![License: BSD NON-AI](https://badgen.net/badge/license/BSD-3%20NON-AI?icon=github)](https://github.com/non-ai-licenses/non-ai-licenses/blob/main/NON-AI-BSD3)

[![Docker Compose Build and Deploy](https://github.com/REF-RAS/rviz_marker_tools/actions/workflows/docker-build.yml/badge.svg)](https://github.com/REF-RAS/rviz_marker_tools/actions/workflows/docker-build.yml)
[![Build Sphinx and Deploy](https://github.com/REF-RAS/rviz_marker_tools/actions/workflows/sphinx.yml/badge.svg)](https://github.com/REF-RAS/rviz_marker_tools/actions/workflows/sphinx.yml)

## Introduction

The `rviz_marker_publisher` is a ROS2 package and a Python API for drawing markers and pointclouds inside visualization tools such as RViz2.  The objective of the package is to hide away the naunces of creating and publishing different types of marker messages, and to provide value-adding services such as marker caching and refreshing, management of topics, publishers, and custom transforms.

The package can significantly reduced the development effort in the following use-cases:
- Real-time scene visualization for system debugging.
    - Define primitives, meshes, and pointcloud for scene visualization and understanding.
    - Use colors, opacity and scales (i.e. dimensions) to represent attributes.
    - Highlight regions, planes, orientations and tracks for plan and collision pereception.
    - Display labels or floating status text next to objects.
    - Define transforms and frames of reference for placing objects into logical groups.
- Interactive visualization for demonstrations. 

### A Simple Script

The following simple script creates a node and then uses the package `rviz_marker_publisher` to publish a sphere marker of size 0.5 at position (0, 0, 0).  There is one line for creating a sphere marker with the desired size, position and colour, and another line for publishing the marker so that a visualizer such as RViz2 can receive and display the marker through the same ROS topic.

```python
import rclpy
from rclpy.node import Node
import rviz_marker
from rviz_marker import RvizMarkerPublisher


def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker.spin_in_thread(the_node)
    # wait for the discovery and matching on the dds layer
    time.sleep(1.0)

    # use rviz_marker_publisher to create and publish a sphere to the default topic for markers
    sphere_marker = rviz_marker.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker) 
```

### Features

- Create and publish the builtin marker types, including sphere, box, cylindar, text, line, path, arrow, and mesh, and pointclouds.
    - Customize the pose, size, colour, lifetime and frame of reference of a marker.
    - Specify the pose with various formats including `Pose`, `PoseStamped`, `xyzrpy`, `xyzqqqq`, and `xyz`.
    - Create a transform between a marker and another reference frame.
- Organize markers into logical sets through marker arrays (`MarkerArray`) or namespace.
- Delete markers, marker arrays and pointclouds.
- Cache selected markers for auto-repeat publishing - late-joining subscribers can still receive them even if the QoS durability of the topic is set to VOLATILE.
- Update the pose of markers and that of the associated transform.
- Add and delete new topics and configure the QoS of the associated publishers.

### Attribution

If this repository has contributed to your work, the Robotics and Autonomous Systems Group suggests that the following statement is to be added to relevant publications or reports.

_"Part of this work was enabled by use of the Robotics and Autonomous Systems Group of the Research Engineering Facility at the Queensland University of Technology (QUT)."_

### Developer

Dr Andrew Lui, Senior Research Engineer <br />
Robotics and Autonomous Systems, Research Engineering Facility <br />
Research Infrastructure <br />
Queensland University of Technology <br />

Latest update: August 2026
