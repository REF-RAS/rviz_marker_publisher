# RViz Marker Publisher: Tutorial Part 1

**Robotics and Autonomous Systems Group, Research Engineering Facility, Research Infrastructure** 
**Queensland University of Technology**

![QUT REF Collection](https://badgen.net/badge/collections/QUT%20REF-RAS?icon=github) 
![ROS2 Package Category](https://badgen.net/badge/category/ROS1%20Package/purple?icon=github)
![Visualization Topic](https://badgen.net/badge/topic/Visualization/orange?icon=github)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

----

## The Basics

To utilize `rviz_marker_publisher` in a ROS2 project, import the package `rviz_marker_publisher` and create an instance of `RvizMarkerPublisher` by passing in the ROS2 node object that uses the `RvizMarkerPublisher` for publishing markers and pointclouds.

```python
...
from rviz_marker_publisher import RvizMarkerPublisher

def main():
    ...
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    ...
```
The following example shows creating the ROS2 node object and using it to create the `RvizMarkerPublisher` instance.

```python
import rclpy
from rclpy.node import Node
from rviz_marker_publisher import RvizMarkerPublisher

def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    ...
```
The RvizMarkerPublisher instance uses time-driven and event-driven asynchronous publishing and the the instance relies on a ROS2 executor to action the publishing. A common method is to call `rclpy.spin()` which will effectively use the main thread as the executor.
```python
def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rclpy.spin()   # blocks indefinitely
    
```
To allow the main function to execute more actions such as creating and publishing a marker, another method is to create a new thread as the executor. The `rviz_marker_publisher` package provides a function `spin_in_thread` that implements the method.

```python
import rviz_marker_publisher
...
def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)    # return after creating a thread as the executor
    
```

The package provides a list of functions for creating different types of marker. The following example creates a sphere marker with the function `create_sphere_marker`.

```python
import rviz_marker_publisher
...
def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)    # return after creating a thread as the executor
    
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
```

The following table lists the parameters for configuration of the sphere markers. The majority of the parameter set is supported by all the marker creator functions.  

| Function parameters | Definition                              | Remarks | 
| :----------------   | :------                              | :------        |
| `name`              | A string indicating the namespace of the marker | Many visualization tools organize markers of the same namespace into a group for control functions |
| `id`                | An integer for identification  | The `name` and `id` together uniquely identify a marker |
| `xyz`               | The position of the sphere in the frame of reference | A 3-tuple (x, y, z) of `float` values |
| `frame_id`          | The frame of reference | default to be the __fixed frame__ of the scene |
| `scale`          | The size of the sphere | a single number of a 3-tuple (lx, ly, lz) indicating the 3-dimensional size |
| `rgba`          | The color | either a 3-tuple (r, g, b) or 4-tuple (r, g, b, a) of `float` values in the range [0, 1] |
| `lifetime`          | The marker will remain visible for this number of seconds | default is 0 meaning it will stay indefinitely |

The marker is not published until it is passed with a function call to `publish`.

```python
import rviz_marker_publisher
...
def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)    # return after creating a thread as the executor
    
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    # publish the marker
    rv.publish(sphere_marker) 
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
```

The above program will publish the marker once and then wait for the Enter key press before moving on or termination.

Another publish option is to cache after publishing and the `RvizMarkerPublisher` instance continues to publish cached markers regularly (the default is a 10 second cycle).

```python
    ...
    
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    # publish the marker
    rv.publish_and_cache(sphere_marker) 
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
```

### Marker Visualization with RViz2

Launch a visualization tool to view the markers.  RViz2 is a visualization tool that can subscribe to the topics publishing markers and pointclouds and display them.  To launch RViz2, execute the command below.

```bash
rviz2
```





## Configure the RvizMarkerPublisher instance




----
### Author

Dr Andrew Lui, Senior Research Engineer <br />
Robotics and Autonomous Systems, Research Engineering Facility <br />
Research Infrastructure <br />
Queensland University of Technology <br />

Latest update: August 2026

