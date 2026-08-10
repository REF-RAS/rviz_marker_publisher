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
import rviz_marker
from rviz_marker import RvizMarkerPublisher, get_logger
logger = get_logger()

def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker.spin_in_thread(the_node)
    # wait for the discovery and matching of publishers and subscribers 
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(2.0)
    # remove existing markers
    logger.info('(reset rviz) remove all in rviz and wait for 2 secs')
    rv.delete_all_objects_by_topics()
    time.sleep(2.0)  
    # add a group of markers for 'work_area'
    sphere_marker = rviz_marker.create_sphere_marker(name='work_area', id=1, xyz=[1, 1, 1], frame_id='map', scale=0.20, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish_and_cache(sphere_marker) 
    axis_marker = rviz_marker.create_axisplane_marker(name='work_area', id=2, bbox2d=[-1, -1, 1, 1], offset=0, frame_id='map', axes='xy', rgba=[0.2, 0.2, 1.0])
    rv.publish_and_cache(axis_marker) 
    arrow_marker = rviz_marker.create_arrow_marker(name='work_area', id=3, xyzrpy=[1, 1, 1, 0, 3.14, 0], frame_id='map', scale=0.50, rgba=[0.0, 1.0, 0.5, 1.0])
    rv.publish_and_cache(arrow_marker)     

    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()