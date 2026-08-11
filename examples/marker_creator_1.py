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
    # add a axis plane marker on xy plane as a marker to the RVizVisualizer
    logger.info('(add) create_axisplane_markers 3 times')
    axis_plane_marker_xy = rviz_marker_publisher.create_axisplane_marker(name='axisplane', id=1, bbox2d=[-1, -1, 1, 1], offset=2, 
                                                               frame_id='map', axes='xy', rgba=[1, 0, 0])
    rv.publish_and_cache(axis_plane_marker_xy)
    # add a axis plane marker on xy plane as a marker to the RVizVisualizer
    axis_plane_marker_xz = rviz_marker_publisher.create_axisplane_marker(name='axisplane', id=2, bbox2d=[-1, -1, 1, 1], offset=2, 
                                                               frame_id='map', axes='xz', rgba=[0, 1, 0])
    rv.publish_and_cache(axis_plane_marker_xz)
    # add a axis plane marker on yz plane as a marker to the RVizVisualizer
    axis_plane_marker_xz = rviz_marker_publisher.create_axisplane_marker(name='axisplane', id=3, bbox2d=[-1, -1, 1, 1], offset=2, 
                                                               frame_id='map', axes='yz', rgba=[0, 0, 1])
    rv.publish_and_cache(axis_plane_marker_xz)     
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()