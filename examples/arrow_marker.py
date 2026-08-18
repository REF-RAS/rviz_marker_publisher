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
    """ Demonstrate how to create arrow markers based on two end positions and based on position and orientation, and how to control the shape of the arrows.
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
    # create and publish a white line marker and two arrow markers
    # the white line marker
    line_marker = rviz_marker_publisher.create_line_marker(name='work_area', id=1, xyz1=[0.0, -0.5, 0], xyz2=[0.0, 1.5, 1.0], frame_id='map', line_width=0.05, rgba=[1.0, 1.0, 1.0, 1.0],)
    rv.publish(line_marker)   
    # the yellow arrow marker
    arrow_marker = rviz_marker_publisher.create_arrow_marker(name='work_area', id=2, xyz1=[-1.5, 0, 0], xyz2=[-1.5, 1, 0], frame_id='map', 
                                                             arrow_head_diameter=0.2, arrow_shaft_diameter=0.1, arrow_head_length=0.05, rgba=[1.0, 1.0, 0.0, 1.0],)
    rv.publish(arrow_marker) 
    # the green arrow marker       
    arrow_marker_again = rviz_marker_publisher.create_arrow_marker_from_xyzrpy(name='work_area', id=3, xyzrpy=[1, 1, 1, 0, 3.14, 0], frame_id='map', 
                                                                arrow_length=0.50, arrow_head_diameter=0.05, rgba=[0.0, 1.0, 0.5, 1.0])
    rv.publish(arrow_marker_again)   
      
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()