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
    # add a sphere marker as a persistent marker to the RVizVisualizer
    logger.info('(add) create sphere marker with transform (tf_frame="sphere.1") and wait for 2 seconds')
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], frame_id='map', scale=0.20, rgba=[1.0, 0.5, 0.5, 0.5])
    rv.publish_and_cache(sphere_marker, pub_tf=True)  # the tf is named 'sphere.1'.
    time.sleep(2.0)  
    # add a cube marker of which the pose is defined in the reference frame of 'sphere.1'
    logger.info('(add) create cube marker at the frame "sphere.1" and wait for 2 seconds')
    cube_marker = rviz_marker_publisher.create_cube_marker_from_bbox(name='cube', id=1, bbox3d=[-0.5, 0.5, -0.5, 0.5, -0.5, 0.5], frame_id='sphere.1', rgba=[0.5, 1.0, 0.5, 0.5])    
    rv.publish_and_cache(cube_marker)
    time.sleep(2.0)  
    # move the sphere to another location, the cube should follow the sphere to the new location
    logger.info('(move) move_marker_xyz by (-1.0, -1.0, 0.0)')
    rviz_marker_publisher.move_marker_xyz(sphere_marker, (-1.0, -1.0, 0.0))
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()
