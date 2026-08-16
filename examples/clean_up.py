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
from rclpy.qos import  QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
from visualization_msgs.msg import Marker, MarkerArray
import rviz_marker_publisher
from rviz_marker_publisher import RvizMarkerPublisher, get_logger
logger = get_logger()

def main():
    # section 1: enable ROS2 node and create the RVizVisualizer 
    rclpy.init()
    the_node:Node = Node(node_name='test_rv_node') 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)
    # section 2: wait for the discovery and matching of publishers and subscribers 
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(2.0)
    # section 3: remove existing markers
    logger.info('(clear objects) remove all markers published earlier on the default topics in rviz')
    rv.delete_all_objects_by_topics()
    # terminate the node
    rclpy.shutdown()

if __name__ == '__main__':
    main()