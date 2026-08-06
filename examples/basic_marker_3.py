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
logger = get_logger('test_rv_mode')

def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizVisualizer(the_node, pub_period_marker=0.1)
    rviz_marker.spin_in_thread(the_node)
    # remove existing markers
    delete_marker = rviz_marker.create_delete_all_marker(reference_frame='map')
    rv.pub_temporary_marker(delete_marker)
    # wait
    logger.info('waiting for 2 seconds')
    time.sleep(2.0)    
    # add a sphere marker as a persistent marker to the RVizVisualizer
    sphere_marker = rviz_marker.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], reference_frame='map', scale=0.40, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.add_persistent_marker(sphere_marker, pub_period=0.4)
    # wait
    logger.info('waiting for 2 seconds')
    time.sleep(2.0)
    # remove existing markers
    delete_marker = rviz_marker.create_delete_all_marker(reference_frame='map')
    rv.pub_temporary_marker(delete_marker)    
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()