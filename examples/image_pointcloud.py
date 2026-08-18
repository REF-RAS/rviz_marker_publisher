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
from sensor_msgs.msg import PointCloud2
from ament_index_python import get_package_share_directory

import rviz_marker_publisher
from rviz_marker_publisher import RvizMarkerPublisher, get_logger
logger = get_logger()

def main():
    """ Demonstrate how to create a PointCloud2 message from an image
        Note: to correctly display the image in RViz, set the Color Transform parameter under PointCloud2 display item to RGB8
    """
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)
    # wait for the discovery and matching of publishers and subscribers 
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(2.0)
    # remove existing markers
    logger.info('(reset rviz) remove all in rviz and wait for 2 secs')
    rv.delete_all_objects_by_topics()
    time.sleep(2.0) 
    # add an image as a pointcloud
    logger.info(f'(add) create_pointcloud_from_image CoralFish.png')
    # NOTE: the image file is in one of the resource folder (examples) defined in setup.py
    image_file = os.path.join(get_package_share_directory('rviz_marker_publisher'), 'examples/assets/CoralFish.png')   
    image_bgr = cv2.imread(image_file)
    image_pointcloud2:PointCloud2 = rviz_marker_publisher.create_pointcloud_from_image(image_bgr, (0, 0.5, 0), pixel_physical_size=[0.002, 0.002, -1], frame_id='map')
    rv.publish(image_pointcloud2)
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()