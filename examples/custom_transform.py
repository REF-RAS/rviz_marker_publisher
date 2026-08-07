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
from geometry_msgs.msg import Pose, Point, Quaternion

import rviz_marker
from rviz_marker import RvizVisualizer, get_logger
logger = get_logger()

def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizVisualizer(the_node)
    rviz_marker.spin_in_thread(the_node)
    # add a custom transform called 'workspace'
    transform_pose = Pose()
    transform_pose.position = Point(x=1.0, y=1.0, z=1.0)
    transform_pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, q=1.0)
    rv.publish_custom_tf('workspace', 'map', transform_pose)
    # add a sphere marker as a persistent marker to the RVizVisualizer
    sphere_marker = rviz_marker.create_sphere_marker(name='sphere', id=1, xyz=[0.5, 0, 0], reference_frame='workspace', scale=0.20, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker) 

    input('Press Enter to terminate')
    rclpy.shutdown()