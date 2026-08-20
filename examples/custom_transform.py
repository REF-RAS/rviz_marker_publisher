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

import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, Point, Quaternion

import rviz_marker_publisher
from rviz_marker_publisher import RvizMarkerPublisher, get_logger
logger = get_logger()

def main():
    """ Demonstrate how to define a custom transform (reference frame) and create a sphere marker based on the transform 
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
    logger.info('(reset rviz) remove all in rviz and wait for 5 secs')
    rv.delete_all_objects_by_topics()
    time.sleep(2.0) 
    # add a custom frame called 'workspace' from the parent frame 'map'
    transform_pose = Pose()
    transform_pose.position = Point(x=1.0, y=1.0, z=1.0)
    transform_pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, q=1.0)
    logger.info(f'(define custom tf) publish_custom_tf "workspace" at {transform_pose}')
    rv.publish_custom_tf('workspace', 'map', transform_pose)
    time.sleep(1.0)
    # add a sphere marker as a persistent marker to the RVizVisualizer
    logger.info('(add) create_sphere_marker in the reference frame "workspace"')
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyzrpy=[0.0, 0.0, 0.0], frame_id='workspace', scale=0.20, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish_and_cache(sphere_marker) 
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()