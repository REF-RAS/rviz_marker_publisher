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
    rv = RvizVisualizer(the_node, pub_marker_cycle=0.1)
    rviz_marker.spin_in_thread(the_node)
    # remove existing markers
    delete_marker = rviz_marker.create_delete_all_marker()
    rv.publish_once(delete_marker)
    # wait
    logger.info('waiting for 2 seconds')
    time.sleep(2.0)  
    # add sphere markers as a temporary marker to the RVizVisualizer
    for i in range(5):
        marker = rviz_marker.create_sphere_marker(name='sphere', id=i, xyz=[1 + i * 0.2, 1, 1], reference_frame='map', scale=0.20, rgba=[1.0, 0.5, 0.5, 1.0])
        rv.publish_once(marker)

    input('Press Enter to terminate')
    rclpy.shutdown()
