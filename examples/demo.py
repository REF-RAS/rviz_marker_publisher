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

import os, sys, random, time, traceback
import cv2
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from geometry_msgs.msg import Pose, Vector3, Point, Quaternion
from sensor_msgs.msg import PointCloud2
import rviz_marker
from rviz_marker import RvizVisualizer, get_logger
logger = get_logger()

def main():
    try:
        rclpy.init()
        the_node = Node(node_name='test_rv_node') 
        # create the RVizVisualizer 
        rv = RvizVisualizer(the_node)
        rviz_marker.spin_in_thread(the_node)
        # wait for the discovery and matching on the dds layer
        logger.info('(wait) discovery and matching of publishers and subscribers')
        time.sleep(3.0)
        # remove existing markers
        logger.info('(reset rviz) remove all in rviz and wait for 2 secs')
        rv.delete_all_objects_by_topics()
        time.sleep(2.0) 
        # start the demo
        logger.info(f'(create frame) world')
        the_pose:Pose = Pose()
        the_pose.position = Point(x=0.0, y=0.0, z=0.0)
        the_pose.orientation = Quaternion(x=.0, y=.0, z=.0, q=1.)
        # create world frame
        rv.publish_custom_tf('world', 'map', the_pose)

        # adding text markers
        logger.info(f'(add) create_text_markers Hello and World')
        text_marker_1 = rv.publish_and_register(rviz_marker.create_text_marker(name='text', id=1, text='Hello', xyzrpy=[0, 0, 0, 0.2, 0, 0], reference_frame='world', scale=0.3), pub_tf=True)
        text_marker_2 = rv.publish_and_register(rviz_marker.create_text_marker(name='text', id=2, text='World', xyzrpy=[0, 1, 0, 0.2, 0, 0], reference_frame='world', scale=0.3), pub_tf=True)
        the_node.get_clock().sleep_for(Duration(seconds=5))
        # add line, sphere and arrow
        logger.info(f'(add) create_line_marker, create_sphere_marker (persistent) and create_arrow_marker (lifetime of 5 secs')
        rv.publish_and_register(line_marker:=rviz_marker.create_line_marker('line', 1, [1, 0, 0], [0, 0, 1], 'world', 0.05, rgba=[0.0, 1.0, 1.0, 1.0]))
        rv.publish_and_register(rviz_marker.create_sphere_marker('sphere', 1, [1, 1, 1], 'world', scale=0.2, rgba=[0.5, 1.0, 1.0, 1.0]))    
        rv.publish_best_effort_once(rviz_marker.create_arrow_marker('arrow', 1, [1.0, 0.0, 0.0, 1.0, 0.0, 0.0], 'world', scale=0.5, lifetime=Duration(seconds=5.0)))
        the_node.get_clock().sleep_for(Duration(seconds=5))
        # delete the line marker
        logger.info(f'(delete) the line')
        the_node.get_clock().sleep_for(Duration(seconds=2))
        rv.delete_object(line_marker)
        the_node.get_clock().sleep_for(Duration(seconds=5))
        # delete all markers
        logger.info(f'(delete) all markers')
        rv.delete_registered_objects_by_topics('/visualization_marker')
        the_node.get_clock().sleep_for(Duration(seconds=5))
        # add a mesh from a stl file
        # computing the full path of the stl file
        # teapot_mesh = 'file://' + os.path.join(os.path.dirname(__file__), 'assets/utah_teapot.stl')
        # teapot_mesh = os.path.join(os.path.dirname(__file__), 'assets/utah_teapot.stl')
        teapot_mesh = 'package://rviz_marker_tools_ros2/examples/assets/utah_teapot.stl' 
        logger.info(f'(add) create_mesh_marker from mesh file location {teapot_mesh}')
        mesh_marker = rviz_marker.create_mesh_marker(name='teapot', id=1, file_uri=teapot_mesh, xyzrpy=[-1.0, -1.0, 0.0, 0, 0, 0], 
                                        reference_frame='map', scale=[0.05, 0.05, 0.05], rgba=[0.5, 1.0, 1.0, 1.0])
        rv.publish_best_effort_once(mesh_marker) 
        the_node.get_clock().sleep_for(Duration(seconds=5))
        # add an image as a pointcloud
        logger.info('(add) create_pointcloud_from_image CoralFish.png')
        image_bgr = cv2.imread(os.path.join(os.path.dirname(__file__), '../docs/assets/CoralFish.png'))
        image_pointcloud2:PointCloud2 = rviz_marker.create_pointcloud_from_image(image_bgr, (0, 0.5, 0), pixel_physical_size=[0.002, 0.002, -1], reference_frame='map')
        rv.publish_best_effort_once(image_pointcloud2)
        the_node.get_clock().sleep_for(Duration(seconds=5))
        # add the text marker and animation
        logger.info(f'[animation] text marker')
        the_node.get_clock().sleep_for(Duration(seconds=2))
        text_marker_1 = rv.publish_best_effort_once(rviz_marker.create_text_marker('text', 1, 'Hello', [0, 0, 0, 0.2, 0, 0], 'world', 0.3))
        for i in range(30):
            xyzrpy = [random.uniform(-0.5, 0.5), None, None, None, None, None]
            rviz_marker.update_marker_xyzrpy(text_marker_1, xyzrpy)
            rv.publish_best_effort_once(text_marker_1)
            the_node.get_clock().sleep_for(Duration(seconds=0.25))
        # delete the text marker again
        rv.delete_object(text_marker_1)

        # create marker array
        logger.info(f'[add marker array] cubes')
        markers_list = []
        for x in range(4):
            for y in range(4):
                xyzrpy=[x * 0.4, y * 0.4, 1.0, 0, 0, 0]
                tile = rviz_marker.create_cube_marker_from_xyzrpy('tile', x + y * 4, xyzrpy, reference_frame='world', 
                                        scale=[0.3, 0.3, 0.05], rgba=[0.0, 0.2, 1.0, 0.5])
                markers_list.append(tile)    
        marker_array = rviz_marker.create_marker_array(markers_list)
        rv.publish_best_effort_once(marker_array)
        the_node.get_clock().sleep_for(Duration(seconds=5, nanoseconds=0))
        # delete all markers
        logger.info(f'[delete all objects]')
        rv.delete_all_objects_by_topics()
        logger.info(f'The demo is completed')
        # pause before terminate until Enter is press
        input('Press Enter to terminate')
        rclpy.shutdown()
    except:
        traceback.print_exc()

if __name__ == '__main__':
    main()