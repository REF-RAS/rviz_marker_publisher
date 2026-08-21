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

import random, time
import rclpy
from rclpy.node import Node
import rviz_marker_publisher
from rviz_marker_publisher import RvizMarkerPublisher, get_logger
logger = get_logger()

def main():
    """ Demonstrate how to create an animation of a sphere marker by randomly changing the marker's x and y position and publishing the marker within a loop  
    """
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)
    # wait for the discovery and matching on the dds layer
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(3.0)
    # remove existing markers
    logger.info('(reset rviz) remove all in rviz and wait for 5 secs')
    rv.delete_all_objects_by_topics()
    time.sleep(2.0) 
    # create a sphere marker and publish it by the RVizVisualizer
    logger.info('(add) create_sphere_marker and wait for 5 seconds')
    xyzrpy = [0, 0, 0, 0, 0, 0]
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyzrpy=xyzrpy, frame_id='map', scale=0.20, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker) 

    # change the pose of the sphere marker in a loop for a basic animation
    logger.info('(animation) move the sphere between x = (-0.5, 0.5) and y = (-0.5, 0.5)')
    for _ in range(100):
        # randomly generate a new x and y values, all other values are unchanged
        xyzrpy = [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), None, None, None, None]
        rviz_marker_publisher.update_marker_xyzrpy(sphere_marker, xyzrpy)
        rv.publish(sphere_marker) 
        time.sleep(0.1)

    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()