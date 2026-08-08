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
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
from visualization_msgs.msg import Marker, MarkerArray
import rviz_marker
from rviz_marker import RvizVisualizer, get_logger
logger = get_logger()

def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizVisualizer(the_node, default_marker_topic='rviz_marker', default_pointcloud_topic='rviz_cloud')
    rviz_marker.spin_in_thread(the_node)
    # wait for the discovery and matching on the dds layer
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(3.0)
    # remove existing markers
    logger.info('(reset rviz) remove all in rviz and wait for 2 secs')
    rv.delete_all_objects_by_topics()
    time.sleep(2.0) 
    logger.info('(add) create_sphere_marker')
    sphere_marker = rviz_marker.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], frame_id='map', 
                                                scale=0.20, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish_and_cache(sphere_marker) 
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()