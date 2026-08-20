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

import os, sys, time
import pytest
import cv2
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from geometry_msgs.msg import Pose, Quaternion, Point
from visualization_msgs.msg import Marker, MarkerArray
from sensor_msgs.msg import PointCloud2
from rclpy.qos import (
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
    QoSProfile,
    QoSReliabilityPolicy,
)
import rviz_marker_publisher
from rviz_marker_publisher import RvizMarkerPublisher, get_logger
logger = get_logger()

@pytest.fixture(scope="session")
def ros_init():
    # initialize ROS 2 context once for the entire test session
    rclpy.init()
    yield
    rclpy.shutdown()

def test_create_node(ros_init):
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)
    # destroy the node
    the_node.destroy_node()
    time.sleep(1.0)

def test_create_markers(ros_init):
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)
    # wait for the discovery and matching of publishers and subscribers 
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(2.0)
    # remove existing markers
    rv.delete_all_objects_by_topics()  
    # test sphere markers
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyzrpy=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker) 
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=2, xyzrpy=[1, 1, 1, 0, 0, 0.5], frame_id='map', scale=[0.5, 0.5, 0.5], rgba=[1.0, 0.5, 0.5, 1.0], lifetime=1.0)
    rv.publish(sphere_marker, delay=1.0) 
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=3, xyzrpy=[1, 1, 1, 0, 0, 0.5])
    rv.publish(sphere_marker, update_stamp=False) 
    # test cylinder markers
    cylinder_marker = rviz_marker_publisher.create_cylinder_marker(name='cylinder', id=1, xyzrpy=[0, 0.5, 0.5, 0, 0, 0], frame_id='map', scale=[0.5, 0.5, 1.5], rgba=[0.0, 1.0, 0.5, 0.5])
    rv.publish_and_cache(cylinder_marker)    
    the_pose:Pose = Pose()
    the_pose.position = Point(x=0.5, y=0.5, z=0.0)
    the_pose.orientation = Quaternion(x=.0, y=.0, z=.0, q=1.)
    cylinder_marker = rviz_marker_publisher.create_cylinder_marker(name='cylinder', id=2, xyzrpy=the_pose, frame_id='map', scale=1.0, rgba=[0.0, 1.0, 0.5], lifetime=10.0)
    rv.publish_and_cache(cylinder_marker)    
    # test cube markers
    cube_marker_1 = rviz_marker_publisher.create_cube_marker_from_bbox(name='cube', id=1, bbox3d=[0, 0, 0, 0.2, 0.2, 0.2], frame_id='map',
                                               rgba=[1.0, 0.5, 0.5, 0.5])
    cube_marker_2 = rviz_marker_publisher.create_cube_marker_from_bbox(name='cube', id=2, bbox3d=[1, 1, 0, 1.5, 1.5, 1.0])
    cuboid_marker_1 = rviz_marker_publisher.create_cube_marker_from_xyzrpy(name='cube', id=1, xyzrpy=[0, 0, 0, 0, 0, 0], frame_id='map', 
                                                scale=0.5, rgba=[1.0, 0.5, 0.5, 0.5])
    cuboid_marker_2 = rviz_marker_publisher.create_cube_marker_from_xyzrpy(name='cube', id=2, xyzrpy=the_pose, frame_id='map',
                                                scale=(0.5, 1.0, 1.5), rgba=[0.0, 0.5, 1.0, 0.5])    
    # test text markers
    text_marker_1 = rviz_marker_publisher.create_text_marker(name='text', id=1, text='Hello', xyzrpy=[0, 0, 0, 0, 0, 0])
    text_marker_2 = rviz_marker_publisher.create_text_marker(name='text', id=2, text='World', xyzrpy=[1.0, 0, 0], frame_id='map', scale=2.0)
    # test line markers
    for i in range(10):
        rviz_marker_publisher.create_line_marker(name='line', id=i, xyz1=[-2.5 + i * 0.5, 0, 0], xyz2=[-2.5 + i * 0.5, 1, 0], frame_id='map',
                                                    line_width=0.05, rgba=[1.0, 1.0, 0.0, 1.0], lifetime=Duration(seconds=5))
    # test arrow markers
    arrow_marker_1 = rviz_marker_publisher.create_arrow_marker(name='arrow', id=1, xyz1=[-1.5, 0, 0], xyz2=[-1.5, 1, 0], frame_id='map', 
                                                             arrow_head_diameter=0.2, arrow_shaft_diameter=0.1, arrow_head_length=0.05, rgba=[1.0, 1.0, 0.0, 1.0],)
    arrow_marker_2 = rviz_marker_publisher.create_arrow_marker(name='arrow', id=2, xyz1=[-1.5, -2, -3.5], xyz2=[0, 0, 0], frame_id='map')
    # test path markers
    path_marker_1 = rviz_marker_publisher.create_path_marker(name='path', id=1, xyzlist=[(0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 0)], frame_id='map',
                                                line_width=0.05, rgba=[1.0, 0.5, 0.5, 0.5])    
    path_marker_2 = rviz_marker_publisher.create_path_marker(name='path', id=2, xyzlist=[(0, 0, 0), (0, 0, 1)])   
    # test mesh marker
    teapot_mesh = 'package://rviz_marker_publisher/examples/assets/utah_teapot.stl' 
    mesh_marker_1 = rviz_marker_publisher.create_mesh_marker(name='teapot', id=1, resource_uri=teapot_mesh, xyzrpy=[-1.0, -1.0, 0.0, 0, 0, 0], 
                                     frame_id='map', scale=[0.10, 0.05, 0.05], rgba=[0.5, 1.0, 1.0, 1.0])  
    rv.publish(mesh_marker_1)
    teapot_mesh = 'file:///workspace/ros2_ws/src/rviz_marker_publisher/examples/assets/utah_teapot.stl' 
    mesh_marker_2 = rviz_marker_publisher.create_mesh_marker(name='teapot', id=1, resource_uri=teapot_mesh, xyzrpy=the_pose, 
                                     frame_id='map', scale=0.05, rgba=[0.5, 1.0, 1.0])    
    rv.publish(mesh_marker_2)    
    # test axisplane marker
    axis_plane_marker_xy = rviz_marker_publisher.create_axisplane_marker(name='axisplane', id=1, bbox2d=[-1, -1, 1, 1], offset=2, 
                                                               frame_id='map', axes='xy', rgba=[1, 0, 0])
    axis_plane_marker_xz = rviz_marker_publisher.create_axisplane_marker(name='axisplane', id=2, bbox2d=[-1, -1, 1, 1], offset=-1.5, 
                                                               frame_id='map', axes='xz', rgba=[0, 1, 0])
    axis_plane_marker_xz = rviz_marker_publisher.create_axisplane_marker(name='axisplane', id=3, bbox2d=[-1, -1, 1, 1], offset=0, 
                                                               frame_id='map', axes='yz', rgba=[0, 0, 1])    
    # destroy the node
    the_node.destroy_node()
    time.sleep(1.0)

def test_create_marker_array_pointcloud(ros_init):
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)
    # wait for the discovery and matching of publishers and subscribers 
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(2.0)
    # remove existing markers
    rv.delete_all_objects_by_topics()  
    # create marker array
    markers_list:list = []
    for x in range(5):
        for y in range(4):
            xyzrpy=[x * 1.0, y * 1.0, 0.0, 0, 0, 0]
            tile = rviz_marker_publisher.create_cube_marker_from_xyzrpy('tile', x + y * 5, xyzrpy, frame_id='map', 
                                    scale=[0.8, 0,8, 0.05], rgba=[0.0, 0.2, 1.0, 0.5],
                                    lifetime=5.0)
            markers_list.append(tile)
    marker_array = rviz_marker_publisher.create_marker_array(markers_list)
    rv.publish_and_cache(marker_array)
    # create pointcloud from image
    image_file = os.path.join('/workspace/ros2_ws/src/rviz_marker_publisher', 'examples/assets/CoralFish.png')   
    image_bgr = cv2.imread(image_file)
    image_pointcloud2:PointCloud2 = rviz_marker_publisher.create_pointcloud_from_image(image_bgr, (0, 0.5, 0), pixel_physical_size=[0.002, 0.002, -1], frame_id='map')
    rv.publish(image_pointcloud2)

    # destroy the node
    the_node.destroy_node()    
    time.sleep(1)

def test_delete_object(ros_init):
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node)
    rviz_marker_publisher.spin_in_thread(the_node)
    # remove existing markers
    rv.delete_all_objects_by_topics() 
    # test sphere markers
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyzrpy=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker) 
    # delete marker
    rv.delete_object(sphere_marker)
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=2, xyzrpy=[1, 1, 1, 0, 0, 0.5], frame_id='map', scale=[0.5, 0.5, 0.5], rgba=[1.0, 0.5, 0.5, 1.0], lifetime=1.0)
    rv.publish(sphere_marker, delay=1.0) 
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=3, xyzrpy=[1, 1, 1, 0, 0, 0.5])
    rv.publish_and_cache(sphere_marker, update_stamp=False)
    # delete marker by id
    rv.delete_marker_by_id('sphere', id=2)
    # delete all
    rv.delete_cached_objects_by_topics()
    # create spehre marker
    for i in range(10):
        sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=i, xyzrpy=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
        rv.publish_and_cache(sphere_marker)     
    # delete all
    rv.delete_all_objects_by_topics()
    # destroy the node
    the_node.destroy_node()    
    time.sleep(1)

def test_constructor(ros_init):
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    callback_group = MutuallyExclusiveCallbackGroup() 
    qos_profile = QoSProfile(durability=QoSDurabilityPolicy.TRANSIENT_LOCAL, reliability=QoSReliabilityPolicy.RELIABLE, 
                             history=QoSHistoryPolicy.KEEP_LAST, depth=10)
    rv = RvizMarkerPublisher(the_node, fixed_frame='map', callback_group=callback_group, default_qos_profile=qos_profile,
                             default_marker_topic='marker', default_marker_array_topic='marker_array', default_pointcloud_topic='pointcloud',
                             refresh_timer_rate=1.0, best_effort_timer_rate=0.005, tf_refresh_timer_rate=0.01, auto_refresh=False)
    rviz_marker_publisher.spin_in_thread(the_node)
    # test sphere markers
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyzrpy=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker) 
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=3, xyzrpy=[1, 1, 1, 0, 0, 0.5])
    rv.publish_and_cache(sphere_marker, update_stamp=False)
    # refresh cached object now
    rv.publish_cached_objects_now()
    # wait
    time.sleep(5.0)
    # destroy the node
    the_node.destroy_node()    
    time.sleep(1)

def test_new_topic(ros_init):
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node, refresh_timer_rate=1.0)
    rviz_marker_publisher.spin_in_thread(the_node)
    # create new topics
    try:
        rv.activate_topic('rviz_marker', Marker)
        rv.activate_topic('rviz_marker_array', MarkerArray)
        rv.activate_topic('rviz_pointcloud', PointCloud2)
    except ValueError:
        raise    
    # test sphere markers
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyzrpy=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish(sphere_marker, topic='rviz_marker') 
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=3, xyzrpy=[1, 1, 1, 0, 0, 0.5])
    rv.publish_and_cache(sphere_marker, update_stamp=False, topic='rviz_marker')
    # create marker array
    markers_list:list = []
    for x in range(5):
        for y in range(4):
            xyzrpy=[x * 1.0, y * 1.0, 0.0, 0, 0, 0]
            tile = rviz_marker_publisher.create_cube_marker_from_xyzrpy('tile', x + y * 5, xyzrpy, frame_id='map', 
                                    scale=[0.8, 0,8, 0.05], rgba=[0.0, 0.2, 1.0, 0.5],
                                    lifetime=5.0)
            markers_list.append(tile)
    marker_array = rviz_marker_publisher.create_marker_array(markers_list)
    rv.publish_and_cache(marker_array, topic='rviz_marker_array')
    # create pointcloud from image
    image_file = os.path.join('/workspace/ros2_ws/src/rviz_marker_publisher', 'examples/assets/CoralFish.png')   
    image_bgr = cv2.imread(image_file)
    image_pointcloud2:PointCloud2 = rviz_marker_publisher.create_pointcloud_from_image(image_bgr, (0, 0.5, 0), pixel_physical_size=[0.002, 0.002, -1], frame_id='map')
    rv.publish(image_pointcloud2, topic='rviz_pointcloud')
    # deactivate topics
    rv.deactivate_topic('rviz_marker')
    rv.deactivate_topic('rviz_marker_array')
    rv.deactivate_topic('rviz_pointcloud')
    # wait
    time.sleep(5.0)
    # destroy the node
    the_node.destroy_node()    
    time.sleep(1)


def test_tf(ros_init):
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizMarkerPublisher(the_node, refresh_timer_rate=1.0)
    rviz_marker_publisher.spin_in_thread(the_node)
    # test sphere markers
    sphere_marker = rviz_marker_publisher.create_sphere_marker(name='sphere', id=1, xyzrpy=[1, 1, 1], frame_id='map', scale=0.50, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish_and_cache(sphere_marker, pub_tf=True)  # sphere.1
    # create axisplane marker using the new frame
    axis_plane_marker_xy = rviz_marker_publisher.create_axisplane_marker(name='axisplane', id=1, bbox2d=[-1, -1, 1, 1], offset=2, 
                                                               frame_id='sphere.1', axes='xy', rgba=[1, 0, 0])
    rv.publish_and_cache(axis_plane_marker_xy, pub_tf=True)
    # create cylinder marker using the new frame
    cylinder_marker = rviz_marker_publisher.create_cylinder_marker(name='path', id=1, xyzrpy=[0, 0.5, 0.5, 0, 0, 0], frame_id='axisplane.1',
                                                scale=[0.5, 0.5, 1.5], rgba=[0.0, 1.0, 0.5, 0.5])    
    rv.publish(cylinder_marker)
    # create custom tf
    transform_pose = Pose()
    transform_pose.position = Point(x=1.0, y=1.0, z=1.0)
    transform_pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, q=1.0)
    rv.publish_custom_tf('workspace', 'map', transform_pose)   
    # create mesh marker 
    teapot_mesh = 'package://rviz_marker_publisher/examples/assets/utah_teapot.stl' 
    mesh_marker_1 = rviz_marker_publisher.create_mesh_marker(name='teapot', id=1, resource_uri=teapot_mesh, xyzrpy=[-1.0, -1.0, 0.0, 0, 0, 0], 
                                     frame_id='workspace', scale=[0.10, 0.05, 0.05], rgba=[0.5, 1.0, 1.0, 1.0])  
    rv.publish(mesh_marker_1)
    rv.publish_custom_tf('robot', 'workspace', transform_pose, static_tf=True)  
    # create cube
    cube_marker_1 = rviz_marker_publisher.create_cube_marker_from_bbox(name='cube', id=1, bbox3d=[0, 0, 0, 0.2, 0.2, 0.2], frame_id='robot',
                                               rgba=[1.0, 0.5, 0.5, 0.5])
    rv.publish(cube_marker_1)    
    # wait
    time.sleep(5.0)
    # destroy the node
    the_node.destroy_node()    
    time.sleep(1)    

# colcon test --packages-select rviz_marker_publisher --pytest-args "-s" --event-handlers console_cohesion+
# colcon test-result --all --verbose

if __name__ == '__main__':
    test()