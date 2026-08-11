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
    # add a mesh from a stl file
    # computing the full path of the stl file
    # teapot_mesh = 'file://' + os.path.join(os.path.dirname(__file__), 'assets/utah_teapot.stl')
    # teapot_mesh = os.path.join(os.path.dirname(__file__), 'assets/utah_teapot.stl')
    teapot_mesh = 'package://rviz_marker_publisher/examples/assets/utah_teapot.stl' 
    logger.info(f'(add) create_mesh_marker from mesh file location {teapot_mesh}')
    mesh_marker = rviz_marker_publisher.create_mesh_marker(name='teapot', id=1, file_uri=teapot_mesh, xyzrpy=[-1.0, -1.0, 0.0, 0, 0, 0], 
                                     frame_id='map', scale=[0.05, 0.05, 0.05], rgba=[0.5, 1.0, 1.0, 1.0])
    rv.publish(mesh_marker) 
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()