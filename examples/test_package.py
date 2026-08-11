#!/usr/bin/env python3

# Copyright 2026 - Andrew Kwok Fai LUI, 
# Robotics and Autonomous Systems Group, REF, RI
# and the Queensland University of Technology

__author__ = 'Andrew Lui'
__copyright__ = 'Copyright 2026'
__license__ = 'Non AI GPL'
__version__ = '1.0'
__email__ = 'ak.lui@qut.edu.au'
__status__ = 'Development'

import os, sys, time
import cv2
import rclpy
from rclpy.node import Node
from ament_index_python import get_package_share_directory
from sensor_msgs.msg import PointCloud2
from visualization_msgs.msg import Marker, MarkerArray
from rosidl_runtime_py.utilities import get_message
import rviz_marker_publisher
from rviz_marker_publisher import RvizMarkerPublisher, get_logger
logger = get_logger()

def find_publishers(node:Node, target_topic:list) -> list[str]:
    # normalize the target_topic input parameter
    if isinstance(target_topic, str):
        target_topic = [target_topic]
    nodes_list = []
    # get a list of all active node names and namespaces
    node_names = node.get_node_names_and_namespaces()
    for name, namespace in node_names:
        # get all topics published by this specific node to return a list of tuples: [('/topic_name', ['types'])]
        pubs = node.get_publisher_names_and_types_by_node(name, namespace)
        for topic_name, topic_types in pubs:
            if topic_name in target_topic:
                full_node_path = f"{namespace}/{name}".replace('//', '/')
                nodes_list.append(full_node_path)
    return full_node_path

def main():
    rclpy.init()
    logger.info('launch the node "test_node"')
    the_node = Node(node_name='test_node') 
    # create the RVizVisualizer 
    logger.info('create the RvizMarkerPublisher object')
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)
    # wait for the discovery and matching on the dds layer
    time.sleep(2.0)
    # publish a marker and a pointcloud
    logger.info('publish a sphere')
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker)    
    logger.info('publish a pointcloud')
    image_file = os.path.join(get_package_share_directory('rviz_marker_publisher'), 'examples/assets/CoralFish.png')
    image_bgr = cv2.imread(image_file)
    image_pointcloud2:PointCloud2 = rviz_marker_publisher.create_pointcloud_from_image(image_bgr, (0, 0.5, 0), pixel_physical_size=[0.002, 0.002, -1], frame_id='map')
    rv.publish(image_pointcloud2)    
    time.sleep(2.0)  
    # search for publishers of the two types of messages at topic /visualization_marker and /visualization_cloud
    nodes_list = find_publishers(the_node, '/visualization_marker')
    logger.info(f'found publishers of /visualization_marker: {nodes_list}')
    nodes_list = find_publishers(the_node, '/visualization_cloud')
    logger.info(f'found publishers of /visualization_cloud: {nodes_list}')    
    # pause before terminate until Enter is press
    time.sleep(10.0)
    logger.info('terminate the test script') 
    rclpy.shutdown()

if __name__ == '__main__':
    main()