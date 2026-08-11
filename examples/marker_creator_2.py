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
import rviz_marker_publisher
from rviz_marker_publisher import RvizMarkerPublisher, get_logger
logger = get_logger()

def main():
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
    # add a small cube marker
    logger.info('(add) create_cube_marker_from_bbox 2 times')
    cube_marker_1 = rviz_marker_publisher.create_cube_marker_from_bbox(name='cube', id=1, bbox3d=[0, 0, 0, 0.2, 0.2, 0.2], frame_id='map',
                                               rgba=[1.0, 0.5, 0.5, 0.5])
    rv.publish_and_cache(cube_marker_1)
    # add a larger cube marker
    cube_marker_2 = rviz_marker_publisher.create_cube_marker_from_bbox(name='cube', id=2, bbox3d=[1, 1, 0, 1.5, 1.5, 1.0], frame_id='map',
                                               rgba=[0.0, 1.0, 0.5, 0.5])
    rv.publish_and_cache(cube_marker_2)

    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()