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

The above example will publish the marker once and then wait for the Enter key press before moving on or termination.

Another publish option is to cache after publishing and the `RvizMarkerPublisher` instance continues to publish cached markers regularly (the default is a 10 second cycle).

```python
    ...
    
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    # publish the marker
    rv.publish_and_cache(sphere_marker) 
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
```

The example script is a node of a ROS2 distributed system that publishes to a ROS2 topic designated for `Markers`. A visualization tool is another node in the same ROS2 distributed system that subscribes to the same topic and displays the marker (see the next section). Usually a short moment is needed for the discovery and matching of publishers and subscribers. The default ROS2 topics used by `RvizMarkerPublisher` are listed in the table below.

| Topic | Message Type                 | QoS | 
| :----------------   | :------         | :------        |
| `/visualization_marker` | `visualization_msgs.msg.Marker`    | `LOCAL_TRANSIENT`, `RELIABLE`, `KEEP_LAST` and a queue of 50 |
| `/visualization_marker_array` | `visualization_msgs.msg.MarkerArray` | `LOCAL_TRANSIENT`, `RELIABLE`, `KEEP_LAST` and a queue of 50 |
| `/visualization_cloud` | `sensor_msgs.msg.PointCloud2`    | `LOCAL_TRANSIENT`, `RELIABLE`, `KEEP_LAST` and a queue of 50 |

Adding a pause between the instantiation of `RvizMarkerPublisher` and the actual publish may be useful sometimes.  See the example below.

```python
    ...
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)    # return after creating a thread as the executor

    # wait for the discovery and matching of publishers and subscribers 
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(2.0)

    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    # publish the marker
    rv.publish(sphere_marker) 
    ...
```

If `rv.publish` is replaced by `rv.publish_and_cache`, the marker is cached and will be published again regularly. A late-joining visualization tool will eventually receive the marker. The pause may be omitted.

Another method to allow late-joining visualization tool to receive the markers published earlier is by defining a new topic with the `LOCAL_TRANSIENT` durability quality-of-service. Note that `RvizMarkerPublisher` is designed to define default topics with the `VOLATILE` durability.

The following example shows how to `activate` a new topic `visualization_marker_persistent` with the `LOCAL_TRANSIENT` durability, and publish the marker on the new topic.

```python
    ...
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)

    qos_profile = QoSProfile(durability=QoSDurabilityPolicy.TRANSIENT_LOCAL, reliability=QoSReliabilityPolicy.RELIABLE, history=QoSHistoryPolicy.KEEP_LAST, depth=50)
    ...
    PERSISTENT_TOPIC_NAME = '/visualization_marker_persistent'
    rv.activate_topic(PERSISTENT_TOPIC_NAME, Marker, qos_profile=qos_profile)
    ...
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker, topic=PERSISTENT_TOPIC_NAME)
```
The marker will be latched, therefore late-joining subscribers will receive and display the marker.

### Marker Visualization with RViz2

A visualization tool is to be launched to view the published markers.  RViz2 is a visualization tool that can subscribe to the topics publishing markers and pointclouds and display them.  To launch RViz2, execute the command below.

```bash
rviz2 
```
RViz2 must be setup in order to receive the markers published by the example program.


## Creating Markers and PointClouds





## Configure the RvizMarkerPublisher instance




----
### Author

Dr Andrew Lui, Senior Research Engineer <br />
Robotics and Autonomous Systems, Research Engineering Facility <br />
Research Infrastructure <br />
Queensland University of Technology <br />

Latest update: August 2026

