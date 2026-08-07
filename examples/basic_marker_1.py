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
    rv = RvizVisualizer(the_node)
    rviz_marker.spin_in_thread(the_node)
    # remove existing markers
    logger.info('(reset rviz) remove all in rviz and wait for 5 secs')
    rv.delete_all_in_rviz_by_topics()
    time.sleep(5.0)   
    # add a sphere marker as a persistent marker to the RVizVisualizer
    logger.info('(add) create_sphere_marker and wait for 5 seconds')
    sphere_marker = rviz_marker.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], reference_frame='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker) 
    time.sleep(5.0) 
    # delete the sphere marker
    # logger.info('(delete) delete the sphere')
    # rv.delete_object(sphere_marker)
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()