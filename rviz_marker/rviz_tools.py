# Copyright 2024 - Andrew Kwok Fai LUI, 
# Robotics and Autonomous Systems Group, REF, RI
# and the Queensland University of Technology

# References for implementation of create_pointcloud_from_image: 
# https://raw.githubusercontent.com/DavidB-CMU/rviz_tools_py/master/src/rviz_tools_py/rviz_tools.py
# https://github.com/eric-wieser/ros_numpy/tree/master/src/ros_numpy
# https://gist.github.com/lucasw/ea04dcd65bc944daea07612314d114bb


__author__ = 'Andrew Lui'
__copyright__ = 'Copyright 2024'
__license__ = 'GPL'
__version__ = '1.0'
__email__ = 'ak.lui@qut.edu.au'
__status__ = 'Development'

import yaml, os, time, numbers, threading, random, traceback
from enum import Enum
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Tuple
import cv2
import numpy as np
import rclpy, tf2_ros
from rclpy.node import Node
from rclpy.task import Future
from rclpy.time import Time
from rclpy.duration import Duration
from rclpy import logging
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.qos import  QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from rclpy.publisher import Publisher
from std_msgs.msg import Header
from tf2_msgs.msg import TFMessage
from std_msgs.msg import ColorRGBA, Header
from geometry_msgs.msg import Pose, PoseStamped, Twist, TwistStamped, Vector3, Point, Quaternion
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
from visualization_msgs.msg import Marker, MarkerArray

from rviz_marker.pose_tools import list_to_pose, pose_to_xyzq
from rviz_marker.package_tools import PackageFile
from rviz_marker.logging_tools import logger
from rviz_marker.lock_tools import synchronized
import rviz_marker.pose_tools as pose_tools

class RGBAColors(int, Enum):
    """ Define common use colours for visualization

    """
    RED = 0, (1.0, 0.0, 0.0, 0.5)
    BLUE = 1, (0.0, 0.0, 1.0, 0.5)
    GREEN = 2, (0.0, 1.0, 0.0, 0.5)
    def __new__(cls, value, rgba='...'):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.rgba = rgba
        return obj
    @staticmethod
    def validate_rgba(rgba):
        rgba = RGBAColors.RED.rgba if rgba is None else rgba
        if type(rgba) in (list, tuple) and len(rgba) == 3:
            rgba.append(1.0)
        return rgba
    
def _create_marker(name:str, id:int, marker_type:int=None, reference_frame:str=None, lifetime=None, 
                        pose=None, scale:list=None, color:list=None) -> Marker:
    """ Create a Marker object
    :meta private:
    :param name: the name space of the marker
    :param id: the id of the marker
    :param reference_frame: the reference frame, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :param pose: the pose of type geometry_msgs.msg.Pose or a list of xyzrpy that is acceptable by list_to_pose of pose_tools
    :param scale: a floating point number of a 3-tuple of floating point indicating the scale
    :param color: a 4-tuple of rgba or 3-tuple of rgb  
    :return: Marker
    """
    the_marker = Marker()
    if reference_frame is not None:
        the_marker.header.frame_id = reference_frame
    # the_marker.header.stamp = Time().to_msg()               # to be populated by the publisher
    the_marker.action = Marker.ADD
    if name is not None:
        the_marker.ns = f'{name}'
        the_marker.id = id
    # the lifetime
    lifetime = Duration(seconds=0) if lifetime is None else lifetime
    if type(lifetime) in (float, int):
        lifetime_ns = int(lifetime * 1e9)
        lifetime = Duration(nanoseconds=lifetime_ns)
    the_marker.lifetime = lifetime.to_msg()
    # the type
    if isinstance(marker_type, int):
        the_marker.type = marker_type
    # the pose
    if isinstance(pose, Pose):
        the_marker.pose = pose
    elif isinstance(pose, (list, tuple)):
        the_marker.pose = list_to_pose(pose)
    # the scale
    if isinstance(scale, numbers.Number):
        scale = [scale, scale, scale]    
    if isinstance(scale, (list, tuple)):
        the_marker.scale = Vector3(x=float(scale[0]), y=float(scale[1]), z=float(scale[2]))
    elif isinstance(scale, Vector3):
        the_marker.scale = scale
    else:
        the_marker.scale = Vector3(x=1.0, y=1.0, z=1.0)
    # the color
    color = RGBAColors.validate_rgba(color)
    the_marker.color = ColorRGBA(r=float(color[0]), g=float(color[1]), b=float(color[2]), a=float(color[3]))       
    return the_marker    
    
def create_delete_marker(name:str, id:int, frame_id:str=None) -> Marker:
    """ Returns a Marker object specified to delete a marker

    :param name: the name space of the marker
    :param id: the id of the marker
    :param reference_frame: the reference frame, defaults to None
    :return: the Marker object for deleting a marker
    """
    the_marker = _create_marker(name, id)
    the_marker.action = Marker.DELETE
    if frame_id is not None:
        the_marker.header.frame_id = frame_id
    return the_marker
    
def create_delete_all_marker(frame_id:str=None) -> Marker:
    """ Returns a Marker object specified to delete all markers

    :param reference_frame: the reference frame, defaults to None
    :return: the Marker object for deleting all markers
    """
    the_marker = Marker()
    the_marker.action = Marker.DELETEALL
    if frame_id is not None:
        the_marker.header.frame_id = frame_id
    return the_marker   

def create_delete_all_marker_array(frame_id:str=None) -> MarkerArray:
    """ Returns a Marker object specified to delete all markers

    :param reference_frame: the reference frame, defaults to None
    :return: the Marker object for deleting all markers
    """
    the_marker_array = MarkerArray()
    the_marker = Marker()
    the_marker.action = Marker.DELETEALL
    if frame_id is not None:
        the_marker.header.frame_id = frame_id
    the_marker_array.markers.append(the_marker) 
    return the_marker_array   

def create_axisplane_marker(name:str, id:int, bbox2d:list, offset:float, reference_frame:str, axes:str='xy', plane_thickness=0.005, 
                             rgba:list=None, lifetime=Duration(seconds=0, nanoseconds=0)) -> Marker:
    """ Creates a marker for displaying a 2D region as a plane

    :param name: the name space of the marker
    :param id: the id of the marker
    :param bbox2d: a bounding box as a list [min_x, min_y, max_x, max_y]
    :param offset: the z value where the plane is display
    :param reference_frame: the reference frame, defaults to None
    :param axes: a string representing the axes where the bounding box lies, defaults to 'xy'
    :param plane_thickness: the thickness of the plane to be displayed, defaults to 0.005
    :param rgba: the colour and alpha value, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :return: the Marker object
    """
    rpy = [0, 0, 0]
    scale1 = abs(bbox2d[2] - bbox2d[0])
    scale2 = abs(bbox2d[3] - bbox2d[1])
    scale1 = 0.01 if scale1 == 0 else scale1
    scale2 = 0.01 if scale2 == 0 else scale2
    if axes == 'xy':
        xyz = [(bbox2d[0] + bbox2d[2]) / 2, (bbox2d[1] + bbox2d[3]) / 2, offset]
        pose = list_to_pose(xyz + rpy)
        scale = (scale1, scale2, plane_thickness)
    elif axes == 'yz':
        xyz = [offset, (bbox2d[0] + bbox2d[2]) / 2, (bbox2d[1] + bbox2d[3]) / 2]
        pose = list_to_pose(xyz + rpy)
        scale = (plane_thickness, scale1, scale2)
    elif axes == 'xz':
        xyz = [(bbox2d[0] + bbox2d[2]) / 2, offset, (bbox2d[1] + bbox2d[3]) / 2]
        pose = list_to_pose(xyz + rpy)
        scale = (scale1, plane_thickness, scale2)
    else:
        logger.warning(f'create_2dregion_marker: invalid plane parameter {axes}')
        return None
    the_marker = _create_marker(name, id, Marker.CUBE, reference_frame, lifetime,
                                pose=pose, scale=scale, color=rgba)
    return the_marker

def create_cube_marker_from_bbox(name:str, id:int, bbox3d:list, reference_frame:str, rgba:list=None, lifetime=rclpy.duration.Duration(seconds=0, nanoseconds=0)) -> Marker:
    """ Creates a marker for displaying a 3D region as a box

    :param name: the name space of the marker
    :param id: the id of the marker
    :param bbox3d: a bounding box as a list [min_x, min_y, min_z, max_x, max_y, max_z]
    :param reference_frame: the reference frame, defaults to None
    :param rgba: the colour and alpha value, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :return: the Marker object
    """
    rpy = [0, 0, 0]
    xyz = [(bbox3d[0] + bbox3d[3]) / 2, (bbox3d[1] + bbox3d[4]) / 2, (bbox3d[2] + bbox3d[5]) / 2]
    pose = list_to_pose(xyz + rpy)
    scale = Vector3(x=float(bbox3d[3] - bbox3d[0]), y=float(bbox3d[4] - bbox3d[1]), z=float(bbox3d[5] - bbox3d[2]))
    the_marker = _create_marker(name, id, Marker.CUBE, reference_frame=reference_frame, lifetime=lifetime,
                                pose=pose, scale=scale, color=rgba) 
    return the_marker

def create_cube_marker_from_xyzrpy(name:str, id:int, xyzrpy:list, reference_frame:str, scale:list=0.5, rgba:list=None, lifetime=Duration(seconds=0, nanoseconds=0)) -> Marker:
    """ Creates a marker for displaying a 3D region as a box

    :param name: the name space of the marker
    :param id: the id of the marker
    :param bbox3d: a bounding box as a list [min_x, min_y, min_z, max_x, max_y, max_z]
    :param reference_frame: the reference frame, defaults to None
    :param rgba: the colour and alpha value, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :return: the Marker object
    """
    pose = list_to_pose(xyzrpy)
    the_marker = _create_marker(name, id, Marker.CUBE, reference_frame, lifetime, pose=pose, scale=scale, color=rgba) 
    return the_marker

def create_arrow_marker(name:str, id:int, xyzrpy:list, reference_frame:str, scale:list=0.5, rgba:list=None, lifetime=Duration(seconds=0, nanoseconds=0)) -> Marker:
    """ Creates a marker for displaying an arrow

    :param name: the name space of the marker
    :param id: the id of the marker
    :param xyzrpy: the pose of the arrow as a list of 6
    :param reference_frame: the reference frame, defaults to None
    :param scale: the thickness of the arrow, defaults to 0.5
    :param rgba: the colour and alpha value, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :return: the Marker object
    """
    pose = list_to_pose(xyzrpy)
    if isinstance(scale, numbers.Number):
        scale = [scale, scale/10, scale/25]
    the_marker = _create_marker(name, id, Marker.ARROW, reference_frame=reference_frame, lifetime=lifetime, pose=pose, scale=scale, color=rgba)    
    return the_marker

def create_line_marker(name:str, id:int, xyz1:list, xyz2:list, reference_frame:str, line_width:float=0.01, rgba:list=None, lifetime=Duration(seconds=0, nanoseconds=0)) -> Marker:
    """ Creates a marker for displaying a line

    :param name: the name space of the marker
    :param id: the id of the marker
    :param xyz1: the first point of the line
    :param xyz2: the second point of the line
    :param reference_frame: the reference frame, defaults to None
    :param line_width: the width of the line, defaults to 0.01
    :param rgba: the colour and alpha value, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :return: the Marker object
    """
    pose = list_to_pose([0, 0, 0, 0, 0, 0])
    scale = [float(line_width), 1.0, 1.0]
    the_marker = _create_marker(name, id, Marker.LINE_STRIP, reference_frame=reference_frame, lifetime=lifetime, pose=pose, scale=scale, color=rgba)  
    the_marker.points[:] = [Point(x=float(xyz1[0]), y=float(xyz1[1]), z=float(xyz1[2])), Point(x=float(xyz2[0]), y=float(xyz2[1]), z=float(xyz2[2]))]
    return the_marker    

def create_path_marker(name:str, id:int, xyzlist:list, reference_frame:str, line_width:float=0.01, rgba:list=None, lifetime=Duration(seconds=0, nanoseconds=0)) -> Marker:
    """ Creates a marker for displaying a path of multiple waypoints

    :param name: the name space of the marker
    :param id: the id of the marker
    :param xyzlist: a list of points (xyz, Pose or PoseStamped) defining the path
    :param reference_frame: the reference frame, defaults to None
    :param line_width: the width of the line, defaults to 0.01
    :param rgba: the colour and alpha value, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :return: the Marker object
    """

    pose = list_to_pose([0, 0, 0, 0, 0, 0])
    scale = [float(line_width), 1.0, 1.0]
    rgba = RGBAColors.RED.rgba if rgba is None else rgba
    the_marker = _create_marker(name, id, Marker.LINE_LIST, reference_frame=reference_frame, lifetime=lifetime, pose=pose, scale=scale, color=rgba)      
    # process the points
    the_marker.points[:] = []
    the_marker.colors[:] = []
    prev_xyz = None
    for i, xyz in enumerate(xyzlist):
        if isinstance(xyz, PoseStamped):
            xyz = [xyz.pose.position.x, xyz.pose.position.y, xyz.pose.position.z]
        elif isinstance(xyz, Pose):
            xyz = [xyz.position.x, xyz.position.y, xyz.position.z]
        elif isinstance(xyz, (tuple, list)):
            pass
        xyz = Point(x=float(xyz[0]), y=float(xyz[1]), z=float(xyz[2]))
        if i == 0: 
            prev_xyz = xyz
            continue
        the_marker.points.append(prev_xyz)
        the_marker.points.append(xyz)
        the_marker.colors.append(ColorRGBA(r=rgba[0], g=rgba[1], b=rgba[2], a=rgba[3]))
        the_marker.colors.append(ColorRGBA(r=rgba[0], g=rgba[1], b=rgba[2], a=rgba[3]))
        prev_xyz = xyz

    return the_marker

def create_sphere_marker(name:str, id:int, xyz:list, reference_frame:str, scale=0.2, rgba:list=None, lifetime=Duration(seconds=0, nanoseconds=0)) -> Marker:
    """ Creates a marker for displaying a sphere

    :param name: the name space of the marker
    :param id: the id of the marker
    :param xyz: the position of the sphere
    :param reference_frame: the reference frame, defaults to None
    :param scale: the scale of the sphere as a list of 3 scales or a number, defaults to 0.2
    :param rgba: the colour and alpha value, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :return: the Marker object
    """
    rpy = [0, 0, 0]
    pose = list_to_pose(xyz + rpy) 
    the_marker = _create_marker(name, id, Marker.SPHERE, reference_frame=reference_frame, lifetime=lifetime, pose=pose, scale=scale, color=rgba)      
    return the_marker

def create_cylinder_marker(name:str, id:int, xyzrpy:list, reference_frame:str, scale=[0.1, 0.1, 0.2], rgba:list=None, lifetime=Duration(seconds=0, nanoseconds=0)) -> Marker:
    """ Creates a marker for displaying a cylinder

    :param name: the name space of the marker
    :param id: the id of the marker
    :param xyzrpy: the pose of the cylinder
    :param reference_frame: the reference frame, defaults to None
    :param scale: the scale of the cylinder as a list of 3 numbers representing radius in x and y direction and the height
    :param rgba: the colour and alpha value, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :return: the Marker object
    """
    pose = list_to_pose(xyzrpy) 
    if type(scale) not in (tuple, list) or any([not isinstance(x, numbers.Number) for x in scale]):
        logger.warning(f'create_cylinder_marker: scale should be a list of 3 numbers (radius, radius, height)')
        return None
    the_marker = _create_marker(name, id, Marker.CYLINDER, reference_frame=reference_frame, lifetime=lifetime, pose=pose, scale=scale, color=rgba)  
    return the_marker 

def create_text_marker(name:str, id:int, text:str, xyzrpy:list, reference_frame:str, scale:list=0.5, rgba:list=None, lifetime=Duration(seconds=0, nanoseconds=0)) -> Marker:
    """ Creates a marker for displaying a text

    :param name: the name space of the marker
    :param id: the id of the marker
    :param text: a string to be displayed
    :param xyzrpy: the pose of the text as a list of 6
    :param reference_frame: the reference frame, defaults to None
    :param scale: the size of the text, defaults to 0.5
    :param rgba: the colour and alpha value, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :return: the Marker object
    """
    pose = list_to_pose(xyzrpy)
    the_marker = _create_marker(name, id, Marker.TEXT_VIEW_FACING, reference_frame=reference_frame, lifetime=lifetime, pose=pose, scale=scale, color=rgba) 
    the_marker.text = text
    return the_marker

def create_mesh_marker(name:str, id:int, file_uri:str, xyzrpy:list, reference_frame:str, scale:list=0.5, rgba:list=None, lifetime=Duration(seconds=0, nanoseconds=0)) -> Marker:
    """ Creates a marker for displaying a mesh object

    :param name: the name space of the marker
    :param id: the id of the marker
    :param file_uri: the full path to the file containing a binary STL or DAE file or using protocols such as file://, package://, or http://
    :param xyzrpy: the pose of the text as a list of 6
    :param reference_frame: the reference frame, defaults to None
    :param scale: the scale factor of the mesh object, defaults to [1, 1, 1]
    :param rgba: the colour and alpha value, defaults to None
    :param lifetime: the duration that the marker is displayed, defaults to rclpy.duration.Duration(seconds=0, nanoseconds=0)
    :return: the Marker object
    """
    pose = list_to_pose(xyzrpy)
    if type(scale) not in (tuple, list) or any([not isinstance(x, numbers.Number) for x in scale]):
        logger.warning(f'create_mesh_marker: scale should be a list of 3 numbers (radius, radius, height)')
        return None

    the_marker = _create_marker(name, id, Marker.MESH_RESOURCE, reference_frame=reference_frame, lifetime=lifetime, pose=pose, scale=scale, color=rgba) 
    try:
        file_uri = PackageFile.resolve_to_valid_uri(file_uri)
    except Exception as ex:
        logger.warning(f'create_mesh_marker: Invalid model_file for object ({file_uri}): {ex}')
        return
    the_marker.mesh_resource = file_uri
    the_marker.mesh_use_embedded_materials = True
    return the_marker

def create_marker_array(markers_list:list[Marker]) -> MarkerArray:
    """ Create a MarkerArray from a list of markers

    :param markers_list: a list of Marker objects
    :type markers_list: list[Marker]
    :return: a MarkerArray populated with the input parameter markers
    :rtype: MarkerArray
    """
    marker_array = MarkerArray()
    if isinstance(markers_list, (list, tuple)):
        for marker in markers_list:
            if isinstance(marker, Marker):
                marker_array.markers.append(marker)
    return marker_array

def create_pointcloud_from_image(image_bgr:np.ndarray, xyz:list=(0, 0, 0), pixel_physical_size:float=0.005, reference_frame=None, opacity=255, depth_array:np.ndarray=None) -> PointCloud2:
    """ Create a PointCloud2 for displaying a OpenCV image (color or greyscale) 

    :param image_bgr: the image to be displayed, type numpy ndarray
    :param xyz: the position of the bottom left hand corner of the image, defaults to (0, 0, 0)
    :param pixel_physical_size: the length of each pixel in x, y, defaults to [0.005, 0.005], and optionally the third value in the list for z scaling factor
    :param reference_frame: the reference frame, defaults to None
    :param opacity: the opacity of the displayed image, defaults to 255
    :param depth_array: optionally a numpy ndarray of exact the same shape as the image indicating the depth, defaults to None
    :return: the PointCloud2 object
    """
    if image_bgr is None:
        logger.error(f'{__name__} (image_to_pointcloud): the parameter image_bgr is None') 
        raise AssertionError('Parameter is None')        
    if depth_array is not None:
        if image_bgr.shape[0] != depth_array.shape[0] or image_bgr.shape[1] != depth_array.shape[1]:
            logger.error(f'{__name__} (image_to_pointcloud): the shape of the parameter depth_array {depth_array.shape} is different from the image_bgr') 
            raise AssertionError('Parameters have different dimensions')
    # fill xyz with default values if it is not a list of 3 numbers
    if xyz is None or type(xyz) not in (list, tuple):
        xyz = [0, 0, 0]
    elif type(xyz) is tuple:
        xyz = list(xyz)
    for _ in range(len(xyz), 3):
        xyz.append(0)
    # fill pixel_physical_size with default values
    default_pixel_physical_size = [0.005, 0.005, 1]
    if pixel_physical_size is None:
        pixel_physical_size = default_pixel_physical_size
    elif isinstance(pixel_physical_size, numbers.Number):
        pixel_physical_size = [pixel_physical_size, pixel_physical_size, 1]
    elif type(pixel_physical_size) in (list, tuple):
        pixel_physical_size = list(pixel_physical_size)
        for i in range(len(pixel_physical_size), 3):
            pixel_physical_size.append(default_pixel_physical_size[i])
    # prepare data structures
    is_grey = len(image_bgr.shape) == 2
    image_height, image_width = image_bgr.shape[0], image_bgr.shape[1]
    num_pixels = image_height * image_width
    if is_grey:
        cloud_data = np.zeros(num_pixels, dtype=[('x', np.float32), ('y', np.float32), ('z', np.float32), ('value', np.uint8)])
    else:
        cloud_data = np.zeros(num_pixels, dtype=[('x', np.float32), ('y', np.float32), ('z', np.float32), ('rgb', np.uint32)])
    # compute the point location for every pixel, for x and y, they are computed from the pixel position scaled by the pixel physical size 
    cloud_data['x'] = np.tile(np.linspace(0, image_width, image_width) * pixel_physical_size[0] + xyz[0], image_height)
    cloud_data['y'] = ((np.repeat(np.linspace(0, image_height, image_height) * pixel_physical_size[1], image_width) - image_height * pixel_physical_size[1]) * -1 + xyz[1])
    if depth_array is None:
        cloud_data['z'] = np.full(num_pixels, xyz[2])
    else:
        cloud_data['z'] = np.reshape(depth_array * pixel_physical_size[2], num_pixels)
    # combine the pixel values into a numpy array of shape (num_pixels, 4) for both greyscale and rgb images
    if is_grey:
        fields = [PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1), PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
          PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1), PointField(name='intensity', offset=12, datatype=PointField.UINT8, count=1),]
        cloud_data['value'] = np.reshape(image_bgr, num_pixels)
    else:
        fields = [PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1), PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
          PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1), PointField(name='rgba', offset=12, datatype=PointField.UINT32, count=1),]
        r = np.asarray(np.reshape(image_bgr[:, :, 2], num_pixels), dtype=np.uint32)
        g = np.asarray(np.reshape(image_bgr[:, :, 1], num_pixels), dtype=np.uint32)
        b = np.asarray(np.reshape(image_bgr[:, :, 0], num_pixels), dtype=np.uint32)   
        cloud_data['rgb'] = np.array((opacity << 24) | (r << 16) | (g << 8) | (b << 0), dtype=np.uint32) 
    # create a PointCloud2 message using the data
    cloud_point_list = cloud_data.tolist()
    return point_cloud2.create_cloud(Header(frame_id = reference_frame), fields, cloud_point_list)

def create_empty_pointcloud(frame_id:str=None):
    fields = [
        PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
        PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
        PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
    ]
    return point_cloud2.create_cloud(Header(frame_id=frame_id), fields, [])

def update_marker_xyzrpy(marker:Marker, xyzrpy:list):
    assert isinstance(xyzrpy, (list, tuple)) and len(xyzrpy) == 6, f'invalid parameter (xyzrpy): expects a list of 6 numbers'
    pose_xyzrpy = pose_tools.pose_to_xyzrpy(marker.pose)
    for index in range(len(xyzrpy)):
        if xyzrpy[index] is None:
            xyzrpy[index] = pose_xyzrpy[index]
    marker.pose = list_to_pose(xyzrpy) 

def move_marker_xyz(marker:Marker, xyz_offset:list):
    assert isinstance(xyz_offset, (list, tuple)) and len(xyz_offset) == 3, f'invalid parameter (xyz_offset): expects a list of 3 numbers'
    for index in range(len(xyz_offset)):
        if xyz_offset[index] is None:
            xyz_offset[index] = 0
    marker.pose.position.x += xyz_offset[0]
    marker.pose.position.y += xyz_offset[1]
    marker.pose.position.z += xyz_offset[2]

# helper function for testing
# call to spin this node 
def spin_in_thread(node:Node) -> None:
    """ create a threaded executor and spin it in a thread 

    """
    executor = rclpy.executors.MultiThreadedExecutor(2)
    executor.add_node(node)            
    executor_thread = threading.Thread(target=executor.spin, daemon=True, args=())
    executor_thread.start()

# --------------------------------------------
# Models a publisher of markers
class PublishTopicManager():
    """ Manage the topics of Marker, MarkerArray and PointCloud2 and the publishers
    """
    def __init__(self, node:Node, default_qos_profile:QoSProfile):
        self._node = node
        self._default_qos_profile = default_qos_profile
        self.topics_dict = defaultdict(lambda: (None, None))         # (topic name) > tuple (message class, publisher)
        self.topics_of_messages = defaultdict(lambda: [])        # (message cls name) > list (topic name)

    @synchronized
    def add_topic_of_message_class(self, topic:str, message_cls:type, qos_profile:QoSProfile=None) -> Publisher:
        assert isinstance(topic, str), f'TopicManager add_topic: invalid parameter type (topic) = {type(topic)}'
        assert isinstance(message_cls, type), f'TopicManager add_topic: invalid parameter type (message_cls) - requires a ros2 visualization message class'
        assert message_cls in (Marker, MarkerArray, PointCloud2), f'TopicManager add_topic: invalid parameter value (message_cls) must be visualization.msgs'
        if topic in self.topics_dict:
            raise ValueError(f'invalid parameter (topic): the topic already used')
        # set qos_profile
        qos_profile = self._default_qos_profile if qos_profile is None else qos_profile
        # create publisher
        pub = self._node.create_publisher(message_cls, topic, qos_profile=qos_profile)
        # update the models: topics_dict
        self.topics_dict[topic] = (message_cls, pub)
        # update the models: topics_of_message_list
        topics_list = self.get_topics_list_of_messages(message_cls)
        topics_list.append(topic)
        message_cls_name = message_cls.__name__
        self.topics_of_messages[message_cls_name] = topics_list
        # return value
        return pub

    @synchronized
    def delete_topic(self, topic:str):
        if topic not in self.topics_dict:
            raise ValueError(f'invalid parameter (topic): the topic not exists')
        message_cls, pub = self.topics_dict[topic]
        # delete from topics_dict
        del self.topics_dict[topic]
        # remove the topic from the list of topics_list_of_messages
        topics_list = self.get_topics_list_of_messages(message_cls)
        if topic in topics_list:
            topics_list.remove(topic)
        # destroy the publisher
        self._node.destroy_publisher(pub)

    def topic_exists(self, topic:str) -> bool:
        return topic in self.topics_dict

    @synchronized
    def get_topics_list_of_messages(self, message_cls:type) -> list:
        message_cls_name = message_cls.__name__
        return self.topics_of_messages.get(message_cls_name, [])

    @synchronized
    def get_publisher_of_topic(self, topic:str) -> Publisher:
        message_cls, pub = self.topics_dict[topic]
        return pub

    @synchronized
    def get_message_cls_of_topic(self, topic:str) -> type:
        message_cls, pub = self.topics_dict[topic]
        return message_cls    

@dataclass
class RvizObjectModel():
    the_object: Any
    topic: str
    pub_time: float = None
    update_stamp: float = True
    tf_frame: str = None
    ns: str = None
    id: int = None

class RvizVisualizer():
    """ A publisher of markers, which handles persistent markers, which is published repeatedly and temporary markers,
        which are published once.
    """
    def __init__(self, node:Node, fixed_frame:str='map', callback_group=None, _default_qos_profile=None, **config_dict):
        """ The constructur

        :param node: the node running this RVizVisualizer object
        :type node: rclpy.Node
        :param callback_group: the callback group or None    
        :param pub_marker_cycle: the default period of publishing marker, defaults to 1.0 second
        :param pub_cloud_cycle: the default period of publishing point cloud, defaults to 1.0 second
        :param topic_marker: the topic used to publish markers, defaults to visualization_marker
        :param topic_cloud: the topic used to publish point cloud, defaults to visualization_cloud     
        """
        self.object_queue_lock = threading.RLock()
        # input parameter
        self._node = node
        self._fixed_frame = fixed_frame
        # constant
        # initialize callback group
        self.callback_group = ReentrantCallbackGroup() if callback_group is None else callback_group
        # create qos profile
        self._default_qos_profile = QoSProfile(durability=QoSDurabilityPolicy.VOLATILE, reliability=QoSReliabilityPolicy.RELIABLE, 
                                        history=QoSHistoryPolicy.KEEP_LAST, depth=50) if _default_qos_profile is None else _default_qos_profile
        # create topic manager
        self.topic_manager = PublishTopicManager(self._node, self._default_qos_profile)
        # set default topics of the three message classes and add the to the topic manager
        self.default_marker_topic = config_dict.get('default_marker_topic', '/visualization_marker')
        self.default_marker_array_topic = config_dict.get('default_marker_array_topic', '/visualization_marker_array')
        self.default_pointcloud_topic = config_dict.get('default_pointcloud_topic', '/visualization_cloud')
        self.topic_manager.add_topic_of_message_class(self.default_marker_topic, Marker)
        self.topic_manager.add_topic_of_message_class(self.default_marker_array_topic, MarkerArray)
        self.topic_manager.add_topic_of_message_class(self.default_pointcloud_topic, PointCloud2)
        logger.info(f'parameter default_marker_topic: "{self.default_marker_topic}" ')
        logger.info(f'parameter default_marker_array_topic: "{self.default_marker_array_topic}" ')     
        logger.info(f'parameter default_pointcloud_topic: "{self.default_pointcloud_topic}" ')
        # state variables
        self.to_refresh_now:bool = False
        self.force_refresh:bool = False
        # set default values for keyword argument
        self.auto_refresh = config_dict.get('auto_refresh', True)    
        self.object_refresh_cycle = config_dict.get('object_refresh_cycle', 10.0)     
        self.best_effort_pub_cycle = config_dict.get('best_effort_pub_cycle', 0.01)               # 100 Hz
        self.tf_refresh_cycle = config_dict.get('tf_refresh_cycle', 0.05)                         # 20 Hz
        logger.info(f'parameter auto_refresh: {self.auto_refresh}')
        logger.info(f'parameter object_refresh_cycle: {self.object_refresh_cycle}')
        logger.info(f'parameter best_effort_pub_cycle: {self.best_effort_pub_cycle}')
        logger.info(f'parameter tf_refresh_cycle: {self.tf_refresh_cycle}')

        # the storage for markers
        self.objects_queue:list[RvizObjectModel] = []                 # RvizObjectModel (topic, the_object, pub_time, tf_frame, ns, id)
        self.best_effort_objects_queue:list[RvizObjectModel] = []    

        self.to_delete_all_pointclouds = False                  # a flag to notify the pointcloud callback to clear all 
        # setup tf publish
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self._node)
        self.tfs_dict = defaultdict(lambda: None)               # frame_name -> dict
     
        # setup timers
        self.timer_tf = self._node.create_timer(self.tf_refresh_cycle, self._cb_timer_tf, callback_group=self.callback_group)
        self.timer_best_effort_pub_cycle = self._node.create_timer(self.best_effort_pub_cycle, self._cb_timer_best_effort, callback_group=self.callback_group)
        self.timer_object_refresh_cycle = self._node.create_timer(self.object_refresh_cycle, self._cb_timer_object_refresh, callback_group=self.callback_group)

    def _get_object_model(self, the_object:Any) -> RvizObjectModel:
        for object_model in self.objects_queue:
            if object_model.the_object == the_object:
                return object_model
        return None

    def _get_ros_time_in_seconds(self, offset:float=None) -> float:
        if not isinstance(offset, numbers.Number):       
            offset = 0
        return self._node.get_clock().now().nanoseconds / 1e9 + offset

    def _cb_timer_best_effort(self):
        with self.object_queue_lock: 
            current_time = self._node.get_clock().now()
            current_time_in_secs = current_time.nanoseconds / 1e9
            object_model:RvizObjectModel
            for object_model in list(self.best_effort_objects_queue):
                # logger.warning(f'_cb_timer_best_effort: {object_model.pub_time is None or current_time_in_secs > object_model.pub_time} {object_model}')
                if object_model.pub_time is None or current_time_in_secs > object_model.pub_time:
                    the_object = object_model.the_object
                    if object_model.update_stamp and isinstance(the_object, (Marker, PointCloud2)):
                        the_object.header.stamp = current_time.to_msg()
                    the_publisher:Publisher = self.topic_manager.get_publisher_of_topic(object_model.topic)
                    the_publisher.publish(the_object)
                    self.best_effort_objects_queue.remove(object_model)

    def _cb_timer_object_refresh(self):
        if not self.auto_refresh and not self.force_refresh:
            return
        with self.object_queue_lock: 
            current_time = self._node.get_clock().now()
            # current_time_in_secs = current_time.nanoseconds / 1e9
            object_model:RvizObjectModel
            for object_model in list(self.objects_queue):
                # logger.warning(f'_cb_timer_object_refresh: {object_model}')
                the_object = object_model.the_object
                if object_model.update_stamp and isinstance(the_object, (Marker, PointCloud2)):
                    the_object.header.stamp = current_time.to_msg()
                the_publisher:Publisher = self.topic_manager.get_publisher_of_topic(object_model.topic)
                the_publisher.publish(the_object)   

    def _cb_timer_tf(self):
        """ internal callback function 
        :meta private:
        """
        with self.object_queue_lock:   
            for custom_tf in self.tfs_dict.values():
                name, parent_frame, pose = custom_tf['frame'], custom_tf['parent_frame'], custom_tf['pose']  
                self._pub_transform(name, pose, parent_frame)  

    # internal function: publish the transform of a specific named object
    def _pub_transform(self, name:str, pose, frame=None):
        """ publish the transform of an object

        :param name: name of the object
        :type name: str
        :param pose: the pose of the object 
        :type pose: Pose, PoseStamped, list of 6 or 7
        :param frame: the frame against which the pose is defined, ignored if PoseStamped is provided, defaults to None
        :type frame: str, optional
        """
        frame = self.base_frame if frame is None else frame
        if type(pose) in [list, tuple]:
            pose_stamped = pose_tools.list_to_pose_stamped(pose, frame)
        elif type(pose) == Pose:
            pose_stamped = PoseStamped()
            pose_stamped.header.frame_id = frame
            pose_stamped.header.stamp = self._node.get_clock().now().to_msg()
            pose_stamped.pose = pose
        elif type(pose) == PoseStamped:
            frame = pose.header.frame_id
            pose_stamped = pose
        else:
            logger.logerr(f'{__class__.__name__}: parameter (pose) is not list of length 6 or 7 or a Pose object -> fix the parameter at behaviour construction')
            raise TypeError(f'A parameter is invalid')
        self.tf_broadcaster.sendTransform(pose_tools.pose_stamped_to_transform_stamped(pose_stamped, name))

    def _get_default_topic(self, the_object:Any) -> str:
        if isinstance(the_object, Marker):
            return self.default_marker_topic
        elif isinstance(the_object, MarkerArray):
            return self.default_marker_array_topic
        elif isinstance(the_object, PointCloud2):
            return self.default_pointcloud_topic
        return None

    def activate_topic(self, topic:str, message_cls:type, qos_profile:QoSProfile=None):
        qos_profile = self._default_qos_profile if qos_profile is None else qos_profile
        self.topic_manager.add_topic_of_message_class(topic, message_cls, qos_profile)

    def deactivate_topic(self, topic:str):
        self.topic_manager.delete_topic(topic)

    def publish_and_register(self, the_object:Any, topic:str=None, pub_tf:bool=False) -> Any:
        """ Publish an object to rviz and again if auto-refresh is true

        :param the_object: A object to be published
        :param topic: the topic to publish to
        :param pub_tf: if True, the pose of the marker is published as a tf frame
        :return: The mrker
        """
        assert isinstance(the_object, (Marker, MarkerArray, PointCloud2)), 'invalid parameter (marker): must be in (Marker, MarkerArray, PointCloud2)'
        topic = self._get_default_topic(the_object) if topic is None else topic
        # raise exception if the topic not found in the topic_manager
        if not self.topic_manager.topic_exists(topic):
            raise ValueError(f'invalid parameter (topic): {topic} not activated')
        # publish the object as soon as possible
        self.publish_best_effort_once(the_object, topic, delay=0.0)
        # create a RvizObjectModel and append to the objects_queue
        with self.object_queue_lock:
            if pub_tf and isinstance(the_object, Marker):
                # create a custom_tf if pub_tf is True and the object is a Marker
                tf_frame = f'{the_object.ns}.{the_object.id}'
                self.publish_custom_tf(tf_frame, the_object.header.frame_id, the_object.pose)
                self.objects_queue.append(RvizObjectModel(the_object=the_object, topic=topic, tf_frame=tf_frame, ns=the_object.ns, id=the_object.id))
            elif isinstance(the_object, Marker):
                # if pub_tf is False and the object is a Marker
                self.objects_queue.append(RvizObjectModel(the_object=the_object, topic=topic, ns=the_object.ns, id=the_object.id))
            else:
                # for other object classes
                self.objects_queue.append(RvizObjectModel(the_object=the_object, topic=topic))
        return the_object
            
    def publish_best_effort_once(self, the_object:Any, topic:str=None, delay:float=None, update_stamp:bool=True) -> Any:
        """ Add an once-only marker, which is to be published only once

        :param marker: A marker to be published only once
        :param delay: The delay     
        :return: The marker
        """
        assert isinstance(the_object, (Marker, MarkerArray, PointCloud2)), 'invalid arameter (marker): must be in (Marker, MarkerArray, PointCloud2)'
        assert delay is None or isinstance(delay, numbers.Number), 'invalid arameter (delay): must be a float (seconds) or None (now)'
        topic = self._get_default_topic(the_object) if topic is None else topic   
        # raise exception if the topic not found in the topic_manager
        if not self.topic_manager.topic_exists(topic):
            raise ValueError(f'invalid parameter (topic): {topic} not activated')
        # create a RvizObjectModel object and append the object to the best_effort_objects_queue         
        pub_time = None if delay is None else self._get_ros_time_in_seconds() + delay
        with self.object_queue_lock:
            # self.best_effort_objects_queue.append({'object': the_object, 'topic': topic, 'pub_time': pub_time})     
            self.best_effort_objects_queue.append(RvizObjectModel(the_object=the_object, topic=topic, pub_time=pub_time, update_stamp=update_stamp))
        return the_object

    def publish_all_objects_again(self) -> None:
        """ publish all the objects once again
        
        """
        def execute_once():
            self.force_refresh = True
            self._cb_timer_object_refresh()
            one_shot_timer.cancel()
            self._node.destroy_timer(one_shot_timer)

        one_shot_timer = self._node.create_timer(0.0, execute_once)
        
    def publish_custom_tf(self, name:str, parent_frame:str, pose:Pose) -> None:
        """ Add a custom transform to the rviz visualizer, which is broadcast regularly

        :param name: the name of the transform
        :param xyz: the xyz pose
        :param rpy: the rpy pose
        :param frame: the reference frame
        """
        if name is None or parent_frame is None or pose is None:
            raise AssertionError(f'RvizVisualizer (add_custom_tf): No parameter can be None')
        self.tfs_dict[name] = {'pose': pose, 'frame':name, 'parent_frame': parent_frame}       
        
    def delete_object(self, the_object:Marker | MarkerArray | PointCloud2):
        """ delete the object from the visualization

        :param the_object: the object
        :type the_object: Marker, MarkerArray or PointCloud2
        """
        assert isinstance(the_object, (Marker, MarkerArray, PointCloud2)), 'invalid arameter (marker): must be in (Marker, MarkerArray, PointCloud2)'
        object_model:RvizObjectModel = self._get_object_model(the_object)
        if object_model is None:
            logger.warning(f'(rviz_tools) delete_object: object not exists')
            return
        with self.object_queue_lock:
            # attempt to send a delete command for the object anyway
            if isinstance(the_object, Marker):
                self._delete_marker(the_object)
            elif isinstance(the_object, MarkerArray):
                self._delete_marker_array(the_object)
            elif isinstance(the_object, PointCloud2):
                self._delete_pointcloud(the_object)
            # delete the cache
            self.objects_queue.remove(object_model)

    # internal function to create delete message for marker deletion 
    def _delete_marker(self, the_object:Marker):
        assert isinstance(the_object, (Marker)), 'invalid parameter (the_object): must be a Marker'
        object_model:RvizObjectModel = self._get_object_model(the_object)
        assert object_model is not None, 'invalid parameter value (the_object):the object not found in the objects queue'
        the_object.action = Marker.DELETE
        self.publish_best_effort_once(object_model.the_object, object_model.topic, delay=0.0)
        # remove tf_frame if defined
        if object_model.tf_frame is not None:
            if object_model.tf_frame in self.tfs_dict:
                del self.tfs_dict[object_model.tf_frame]

    # internal function to create delete all message for marker_array deletion 
    def _delete_marker_array(self, the_object:Marker):
        assert isinstance(the_object, (MarkerArray)), 'invalid arameter (the_object): must be a MarkerArray'
        object_model:RvizObjectModel = self._get_object_model(the_object)
        assert object_model is not None, 'invalid parameter value (the_object):the object not found in the objects queue'
        self.publish_best_effort_once(create_delete_all_marker_array(), object_model.topic, delay=0.0)

    # internal function to create empty pointcloud message for pointcloud deletion 
    def _delete_pointcloud(self, the_object:Marker):
        assert isinstance(the_object, (MarkerArray)), 'invalid arameter (the_object): must be a PointCloud'
        object_model:RvizObjectModel = self._get_object_model(the_object)
        assert object_model is not None, 'invalid parameter value (the_object):the object not found in the objects queue'
        self.publish_best_effort_once(create_empty_pointcloud(), object_model.topic, delay=0.0)        
            
    def delete_registered_objects_by_topics(self, topics_list:list=None):
        """ delete all objects from rviz, optionally only the topics in the topics_list

        :param topics_list: the topics included, defaults to None (all default topics)
        :type topics_list: list, optional
        """
        if topics_list is None:
            topics_list = [self.default_marker_topic, self.default_marker_array_topic, self.default_pointcloud_topic]
        elif isinstance(topics_list, str):
            topics_list = [topics_list]
        assert isinstance(topics_list, (list, tuple)), 'invalid parameter type (topics_list): must be a str, a list of str, or None'
        # topics deleted are not deleted again
        topics_deleted_list = []
        # iterate through the objects_queue
        object_model: RvizObjectModel
        with self.object_queue_lock:
            for object_model in list(self.objects_queue):
                if object_model.topic in topics_list:
                    if object_model.topic not in topics_deleted_list:
                        self.delete_object(object_model.the_object)
                        topics_deleted_list.append(object_model.topic)

    def delete_all_objects_by_topics(self, topics_list:list[str]=None, frame_id:str=None):
        """ attempt to clear old objects by sending DELETE_ALL messages to the topics

        :param topics_list: the list of topics to send DELETE_ALL messages, defaults to None (the default topics)
        :type topics_list: list[str], optional
        :param frame_id: the frame id, defaults to the default the fixed_frame variable of this object
        :type frame_id: str, optional
        """
        if topics_list is None:
            topics_list = [self.default_marker_topic, self.default_marker_array_topic, self.default_pointcloud_topic]
        elif isinstance(topics_list, str):
            topics_list = [topics_list]
        assert isinstance(topics_list, (list, tuple)), 'invalid parameter type (topics_list): must be a str, a list of str, or None'
        # set default frame_id if needed
        frame_id = self._fixed_frame if frame_id is None else frame_id
        # iterate through the topics_list
        for topic in topics_list:
            message_cls = self.topic_manager.get_message_cls_of_topic(topic)
            if message_cls is None:
                continue
            if message_cls == Marker:
                self.publish_best_effort_once(create_delete_all_marker(frame_id=frame_id), topic, update_stamp=True)
            elif message_cls == MarkerArray:
                self.publish_best_effort_once(create_delete_all_marker_array(frame_id=frame_id), topic, update_stamp=False)
            elif message_cls == PointCloud2:
                self.publish_best_effort_once(create_empty_pointcloud(frame_id=frame_id), topic, update_stamp=False)

    def audit_rviz_subscriptions(self) -> dict[str, list] | None:
        """ audit the rviz node and query the topic subscription

        :return: a dictionary containing key value pairs of (topic name, list of message type names) or None if the query failed
        :rtype: dict[str, list] or None
        """
        node_list = self._node.get_node_names_and_namespaces()
        # check if rviz2 is found
        rviz_node = None
        for name, namespace in node_list:
            if 'rviz2' in name.lower():
                rviz_node = (name, namespace)
                break
        # if rviz2 node is found, query the topic subscription of the node
        if rviz_node:
            node_name, node_ns = rviz_node
            try:
                subscriptions = self._node.get_subscriber_names_and_types_by_node(node_name, node_ns)
                return {topic: message_names_list for topic, message_names_list in subscriptions}
            except Exception as e:
                ...
        return None
        

        





