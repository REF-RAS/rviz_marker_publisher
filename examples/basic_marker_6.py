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
from rclpy.duration import Duration
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
    delete_marker = rviz_marker.create_delete_all_marker()
    rv.publish_once(delete_marker)
    # wait
    logger.info('waiting for 2 seconds')
    time.sleep(2.0)  
    # add line markers as a temporary marker to the RVizVisualizer with a different lifetime
    for i in range(10):
        rv.publish_once(rviz_marker.create_line_marker(name='line', id=i, xyz1=[i * 0.5, 0, 0], xyz2=[i * 0.5, 1, 0], reference_frame='map',
                                                    line_width=0.02, rgba=[1.0, 1.0, 0.0, 1.0], lifetime=Duration(seconds=1))) 
 
    input('Press Enter to terminate')
    rclpy.shutdown()