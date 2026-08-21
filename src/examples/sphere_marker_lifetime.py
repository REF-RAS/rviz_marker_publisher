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
import rviz_marker_publisher
from rviz_marker_publisher import RvizMarkerPublisher, get_logger
logger = get_logger()

def main():
    """ Demonstrate how to define a marker with a finite lifetime when the marker will be auto-deleted
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
    logger.info('(reset rviz) remove all in rviz and wait for 2 secs')
    rv.delete_all_objects_by_topics()
    time.sleep(2.0)    
    # create a sphere marker with a lifetime of 5 seconds
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyzrpy=[1, 1, 1], frame_id='map', scale=0.40, rgba=[1.0, 0.5, 0.5, 1.0],
                                                               lifetime=5.0)
    rv.publish(sphere_marker)
    # wait
    logger.info('waiting for 10 seconds')
    time.sleep(10.0)
    # remove existing markers
    rv.delete_cached_objects_by_topics()   
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()