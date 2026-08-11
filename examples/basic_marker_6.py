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
from rclpy.duration import Duration
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
    # add line markers as a temporary marker to the RVizVisualizer with a different lifetime
    logger.info('(add) create_line_marker with lifetime of 5 seconds 10 times (ensure the rviz Marker topic has depth >= 10)')    
    for i in range(10):
        rv.publish(rviz_marker_publisher.create_line_marker(name='line', id=i, xyz1=[-2.5 + i * 0.5, 0, 0], xyz2=[-2.5 + i * 0.5, 1, 0], frame_id='map',
                                                    line_width=0.05, rgba=[1.0, 1.0, 0.0, 1.0], lifetime=Duration(seconds=5))) 
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()