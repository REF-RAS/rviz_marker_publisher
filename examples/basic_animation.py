#!/usr/bin/env python3

# Copyright 2024 - Andrew Kwok Fai LUI, 
# Robotics and Autonomous Systems Group, REF, RI
# and the Queensland University of Technology

__author__ = 'Andrew Lui'
__copyright__ = 'Copyright 2024'
__license__ = 'GPL'
__version__ = '1.0'
__email__ = 'ak.lui@qut.edu.au'
__status__ = 'Development'

import time
import rclpy
from rclpy.node import Node
import rviz_marker
from rviz_marker import RvizVisualizer, get_logger
logger = get_logger()

def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizVisualizer(the_node, pub_marker_cycle=0.005)       # NOTE: the 0.005 gives a faster refresh rate for the animation
    rviz_marker.spin_in_thread(the_node)
    # remove existing markers
    delete_marker = rviz_marker.create_delete_all_marker(reference_frame='map')
    rv.publish_once(delete_marker)
    # wait
    logger.info('waiting for 2 seconds')
    time.sleep(2.0)  
    # add a sphere marker as a persistent marker to the RVizVisualizer
    sphere_marker = rviz_marker.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], reference_frame='map', scale=0.20, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker, pub_cycle=0.1) 

    # change the pose of the sphere marker in a loop for a basic animation
    dx = 0.1
    for i in range(100):
        pose = sphere_marker.pose
        dx = -dx if pose.position.x < 0.0 or pose.position.x > 3.0 else dx
        pose.position.x += dx  # change the x position
        time.sleep(0.1)

    input('Press Enter to terminate')
    rclpy.shutdown()