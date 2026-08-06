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
    sphere_marker = rviz_marker.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], reference_frame='map', scale=0.20, rgba=[1.0, 0.5, 0.5, 0.5])
    rv.add_persistent_marker(sphere_marker, pub_tf=True)  # the tf is named 'sphere.1'.
    # add a cube marker of which the pose is defined in the reference frame of 'sphere.1'
    cube_marker = rviz_marker.create_cube_marker_from_bbox(name='cube', id=1, bbox3d=[-0.5, 0.5, -0.5, 0.5, -0.5, 0.5], reference_frame='sphere.1', rgba=[0.5, 1.0, 0.5, 0.5])    
    rv.add_persistent_marker(cube_marker)
    # wait
    logger.info('waiting for 2 seconds')
    time.sleep(2.0)  
    # move the sphere to another location, the cube should follow the sphere to the new location
    pose = sphere_marker.pose
    pose.position.x = -1.0
    pose.position.y = -1.0
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()
