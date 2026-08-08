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
    rv = RvizVisualizer(the_node)
    rviz_marker.spin_in_thread(the_node)
    # wait for the discovery and matching on the dds layer
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(3.0)
    # remove existing markers
    logger.info('(reset rviz) remove all in rviz and wait for 2 secs')
    rv.delete_all_objects_by_topics()
    time.sleep(2.0) 
    # add a small cube marker
    logger.info('(add) create_cube_marker_from_xyzrpy 2 times')
    cuboid_marker_1 = rviz_marker.create_cube_marker_from_xyzrpy(name='cube', id=1, xyzrpy=[0, 0, 0, 0, 0, 0], frame_id='map',
                                                scale=0.5, rgba=[1.0, 0.5, 0.5, 0.5])
    rv.publish_and_cache(cuboid_marker_1)
    # add a larger cube marker
    cuboid_marker_2 = rviz_marker.create_cube_marker_from_xyzrpy(name='cube', id=2, xyzrpy=[2.0, 2.0, 0.5, 1.2, 0.0, 1.2], frame_id='map',
                                                scale=1.0, rgba=[0.0, 0.5, 1.0, 0.5])
    rv.publish_and_cache(cuboid_marker_2)
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()