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

import os, sys, time, random, traceback
import cv2
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from geometry_msgs.msg import Pose, Point, Quaternion
from visualization_msgs.msg import MarkerArray

import rviz_marker
from rviz_marker import RvizVisualizer, get_logger
logger = get_logger()

# -- the test program
def main():
    try:
        rclpy.init()
        the_node = Node(node_name='test_rv_node')   
        # test the mark visualization
        rv = RvizVisualizer(the_node, pub_marker_cycle=0.005)       # NOTE: the 0.005 gives a faster refresh rate for the animation
        rviz_marker.spin_in_thread(the_node)
        # remove existing markers
        logger.info(f'[delete all markers]')
        rv.delete_all_in_rviz()
        # wait
        logger.info('[waiting]: 2 seconds')
        time.sleep(2.0)
        # start the demo
        logger.info(f'[create frame]: world')
        the_pose:Pose = Pose()
        the_pose.position = Point(x=0.0, y=0.0, z=0.0)
        the_pose.orientation = Quaternion(x=.0, y=.0, z=.0, q=1.)
        # create world frame
        rv.publish_custom_tf('world', 'map', the_pose)

        # adding text markers
        logger.info(f'[add text markers] Hello and World')
        text_marker_1 = rv.publish(rviz_marker.create_text_marker(name='text', id=1, text='Hello', xyzrpy=[0, 0, 0, 0.2, 0, 0], reference_frame='world', scale=0.3), pub_tf=True)
        text_marker_2 = rv.publish(rviz_marker.create_text_marker(name='text', id=2, text='World', xyzrpy=[0, 1, 0, 0.2, 0, 0], reference_frame='world', scale=0.3), pub_tf=True)

        # add line, sphere and arrow
        logger.info(f'[add markers] line, sphere (persistent) and arrow (5 seconds)')
        rv.publish(rviz_marker.create_line_marker('line', 1, [1, 0, 0], [0, 0, 1], 'world', 0.05, rgba=[0.0, 1.0, 1.0, 1.0]), pub_cycle=0.1)
        rv.publish(rviz_marker.create_sphere_marker('sphere', 1, [1, 1, 1], 'world', scale=0.2, rgba=[0.5, 1.0, 1.0, 1.0]))    
        rv.publish_once(rviz_marker.create_arrow_marker('arrow', 1, [1.0, 0.0, 0.0, 1.0, 0.0, 0.0], 'world', lifetime=Duration(seconds=5.0)))
        the_node.get_clock().sleep_for(Duration(seconds=5))
        # delete the line marker
        logger.info(f'[delete marker] line')
        the_node.get_clock().sleep_for(Duration(seconds=2))
        rv.delete_object('line', 1)
        the_node.get_clock().sleep_for(Duration(seconds=5))
        # delete all markers
        logger.info(f'[delete all markers]')
        rv.delete_all_markers()
        the_node.get_clock().sleep_for(Duration(seconds=5))
        # display stl mesh file
        # ogger.info(f'[add marker] teapot mesh')
        # teapot_mesh = os.path.join(os.path.dirname(__file__), '../docs/assets/UtahTeapot.stl')
        # teapot_mesh = 'file://' + teapot_mesh
        # rv.add_persistent_marker(rviz_marker.create_mesh_marker('teapot', 1, teapot_mesh, [-1.0, -1.0, 0.0, 0, 0, 0], 'world', [0.05, 0.05, 0.05], rgba=[0.5, 1.0, 1.0, 1.0]))  
        # display image as pointcloud
        logger.info(f'[add marker] coral fish image')
        image_bgr = cv2.imread(os.path.join(os.path.dirname(__file__), '../docs/assets/CoralFish.png'))
        pc2_message = rviz_marker.create_pointcloud_from_image(image_bgr, (0, 0.5, 0), pixel_physical_size=[0.002, 0.002, -1], reference_frame='world')
        rv.pub_pointcloud('the_image', pc2_message)
        
        # add the text marker and animation
        logger.info(f'[animation] text marker')
        the_node.get_clock().sleep_for(Duration(seconds=2))
        text_marker_1 = rv.publish(rviz_marker.create_text_marker('text', 1, 'Hello', [0, 0, 0, 0.2, 0, 0], 'world', 0.3), pub_cycle=0.1, pub_tf=True)
        for i in range(30):
            pose = text_marker_1.pose
            pose.position.x += random.uniform(-0.5, 0.5)
            the_node.get_clock().sleep_for(Duration(seconds=1))
        # delete the text marker again
        rv.delete_object('text', 1)

        # create marker array
        logger.info(f'[add marker array] cubes')
        marker_array = MarkerArray()
        for x in range(4):
            for y in range(4):
                xyzrpy=[x * 0.4, y * 0.4, 1.0, 0, 0, 0]
                tile = rviz_marker.create_cube_marker_from_xyzrpy('tile', x + y * 4, xyzrpy, reference_frame='world', 
                                        scale=[0.3, 0.3, 0.05], rgba=[0.0, 0.2, 1.0, 0.5])
                marker_array.markers.append(tile)    
        rv.pub_marker_array('4x4', marker_array)

        # delete all markers
        logger.info(f'[delete all marker array]')
        the_node.get_clock().sleep_for(Duration(seconds=5, nanoseconds=0))
        rv.delete_all_marker_arrays()
        logger.info(f'The demo is completed')

        input('Press Enter to terminate')
        rclpy.shutdown()
    except:
        traceback.print_exc()

if __name__ == '__main__':
    main()