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
    else:
        the_marker.scale = Vector3(x=1.0, y=1.0, z=1.0)
    # the color
    color = RGBAColors.validate_rgba(color)
    the_marker.color = ColorRGBA(r=color[0], g=color[1], b=color[2], a=color[3])       
    return the_marker    
    
def create_delete_marker(name:str, id:int) -> Marker:
    """ Returns a Marker object specified to delete a marker

    :param name: the name space of the marker
    :param id: the id of the marker
    :param reference_frame: the reference frame, defaults to None
    :return: the Marker object for deleting a marker
    """
    the_marker = _create_marker(name, id)
    the_marker.action = Marker.DELETE
    return the_marker
    
def create_delete_all_marker() -> Marker:
    """ Returns a Marker object specified to delete all markers

    :param reference_frame: the reference frame, defaults to None
    :return: the Marker object for deleting all markers
    """
    the_marker = _create_marker(None, None)
    the_marker.action = Marker.DELETEALL
    return the_marker   

def create_delete_all_marker_array() -> MarkerArray:
    """ Returns a Marker object specified to delete all markers

    :param reference_frame: the reference frame, defaults to None
    :return: the Marker object for deleting all markers
    """
    the_marker_array = MarkerArray()
    the_marker = _create_marker(None, None)
    the_marker.action = Marker.DELETEALL
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
        scale = Vector3(x=float(scale1), y=float(scale2), z=float(plane_thickness))
    elif axes == 'yz':
        xyz = [offset, (bbox2d[0] + bbox2d[2]) / 2, (bbox2d[1] + bbox2d[3]) / 2]
        pose = list_to_pose(xyz + rpy)
        scale = Vector3(x=float(plane_thickness), y=float(scale1), z=float(scale2))
    elif axes == 'xz':
        xyz = [(bbox2d[0] + bbox2d[2]) / 2, offset, (bbox2d[1] + bbox2d[3]) / 2]
        pose = list_to_pose(xyz + rpy)
        scale = Vector3(x=float(scale1), y=float(plane_thickness), z=float(scale2))
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
        file_uri = PackageFile.resolve_to_file_or_http_uri(file_uri)
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

def create_empty_pointcloud():
    fields = [
        PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
        PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
        PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
    ]
    return point_cloud2.create_cloud(Header(), fields, [])

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
        self.topics_list_of_messages = defaultdict(lambda: [])        # (message cls name) > list (topic name)

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
        self.topics_list_of_messages[message_cls_name] = topics_list
        # return value
        return pub

    def get_topics_list_of_messages(self, message_cls:type) -> list:
        message_cls_name = message_cls.__name__
        return self.topics_list_of_messages.get(message_cls_name, [])

    def get_publisher_of_topic(self, topic:str) -> Publisher:
        message_cls, pub = self.topics_dict[topic]
        return pub

class RvizVisualizer():
    """ A publisher of markers, which handles persistent markers, which is published repeatedly and temporary markers,
        which are published once.
    """
    def __init__(self, node:Node, callback_group=None, **config_dict):
        """ The constructur

        :param node: the node running this RVizVisualizer object
        :type node: rclpy.Node
        :param callback_group: the callback group or None    
        :param pub_marker_cycle: the default period of publishing marker, defaults to 1.0 second
        :param pub_cloud_cycle: the default period of publishing point cloud, defaults to 1.0 second
        :param topic_marker: the topic used to publish markers, defaults to visualization_marker
        :param topic_cloud: the topic used to publish point cloud, defaults to visualization_cloud     
        """
        self.lock = threading.RLock()
        # input parameter
        self._node = node
        # constant
        # initialize callback group
        self.callback_group = ReentrantCallbackGroup() if callback_group is None else callback_group
        # create qos profile
        self._default_qos_profile = QoSProfile(durability=QoSDurabilityPolicy.TRANSIENT_LOCAL, reliability=QoSReliabilityPolicy.BEST_EFFORT, history=QoSHistoryPolicy.KEEP_LAST, depth=5)
        # create topic manager
        self.topic_manager = PublishTopicManager(self._node, self._default_qos_profile)
        # set default topics of the three message classes and add the to the topic manager
        self.default_marker_topic = config_dict.get('default_marker_topic', '/visualization_marker')
        self.default_marker_array_topic = config_dict.get('default_marker_array_topic', '/visualization_marker_array')
        self.default_pointcloud_topic = config_dict.get('default_pointcloud_topic', '/visualization_cloud')
        self.topic_manager.add_topic_of_message_class(Marker, self.default_marker_topic)
        self.topic_manager.add_topic_of_message_class(MarkerArray, self.default_marker_array_topic)
        self.topic_manager.add_topic_of_message_class(PointCloud2, self.default_pointcloud_topic)
        logger.info(f'parameter default_marker_topic: "{self.default_marker_topic}" ')
        logger.info(f'parameter default_marker_array_topic: "{self.default_marker_array_topic}" ')     
        logger.info(f'parameter default_pointcloud_topic: "{self.default_pointcloud_topic}" ')
        # state variables
        self.to_refresh_now:bool = False

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
        self.objects_dict = defaultdict(lambda: None)  # (marker_namespace, marker_id) -> marker dict (topic, object, class (marker/marker_array/pointcloud), pub_time)
        self.best_effort_objects_queue:list = []       # marker dict (topic, marker/marker_array/pointcloud, pub_time)

        self.to_delete_all_pointclouds = False                  # a flag to notify the pointcloud callback to clear all 
        # setup tf publish
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self._node)
        self.tfs_dict = defaultdict(lambda: None)               # frame_name -> dict
     
        # setup timers
        self.timer_tf = self._node.create_timer(self.tf_refresh_cycle, self._cb_timer_tf, callback_group=self.callback_group)
        self.timer_best_effort_pub_cycle = self._node.create_timer(self.best_effort_pub_cycle, self._cb_timer_best_effort, callback_group=self.callback_group)
        self.timer_object_refresh_cycle = self._node.create_timer(self.object_refresh_cycle, self._cb_timer_object_refresh, callback_group=self.callback_group)

        # self.timer_marker_viz = self._node.create_timer(self.object_refresh_cycle, self._cb_timer_marker_viz, callback_group=self.callback_group)
        # self.timer_cloud_viz = self._node.create_timer(self.default_pub_cloud_cycle, self._cb_timer_cloud_viz, callback_group=self.callback_group)
        # self.timer_tf = self._node.create_timer(self.tf_refresh_cycle, self._cb_timer_tf, callback_group=self.callback_group)
        # self.timer_once_marker_viz = self._node.create_timer(self.default_pub_once_marker_cycle, self._cb_timer_once_marker_viz, callback_group=self.callback_group)

    def _get_ros_time_in_seconds(self, offset:float=None) -> float:
        if not isinstance(offset, numbers.Number):       
            offset = 0
        return self._node.get_clock().now().nanoseconds / 1e9 + offset

    def _cb_timer_best_effort(self):
        with self.lock: 
            current_time = self._node.get_clock().now()
            current_time_in_secs = current_time.nanoseconds / 1e9
            for marker_dict in list(self.best_effort_objects_queue):
                topic, the_object, message_cls, pub_time = marker_dict['topic'], marker_dict['object'], marker_dict['message_cls'], marker_dict['pub_time']
                if marker_dict['pub_time'] is None or current_time_in_secs > marker_dict['pub_time']:
                    the_object.header.stamp = current_time.to_msg()
                    the_publisher:Publisher = self.topic_manager.get_publisher_of_topic(topic)
                    the_publisher.publish(the_object)
                    self.best_effort_objects_queue.remove(marker_dict)

    def _cb_timer_once_marker_viz(self):
        """ internal callback function 
        :meta private:
        """
        with self.lock: 
            current_time = self._node.get_clock().now()
            current_time_in_secs = current_time.nanoseconds / 1e9
            # publish the once-off markers
            for marker_dict in list(self.once_marker_list):
                marker = marker_dict['marker']
                if marker_dict['pub_time'] is None or current_time_in_secs > marker_dict['pub_time']:
                    marker.header.stamp = current_time.to_msg()
                    self.marker_pub.publish(marker)
                    self.once_marker_list.remove(marker_dict)
            # publish the once-off marker arrays
            for marker_dict in list(self.once_marker_array_list):
                marker_array = marker_dict['marker_array']
                if marker_dict['pub_time'] is None or current_time_in_secs > marker_dict['pub_time']:
                    marker.header.stamp = current_time.to_msg()
                    self.marker_array_pub.publish(marker_array)
                    self.once_marker_array_list.remove(marker_dict)  

    def _cb_timer_marker_viz(self):
        """ internal callback function 
        :meta private:
        """
        with self.lock: 
            # publish the persistent markers of which the pub_cycle has lapsed   
            current_time = self._node.get_clock().now()
            current_time_in_secs = current_time.nanoseconds / 1e9
            for key in self.markers_dict.keys():
                marker_dict = self.markers_dict.get(key)
                marker = marker_dict['marker'] 
                if marker_dict['next_time'] is None or current_time_in_secs >= marker_dict['next_time']:
                    marker.header.stamp = current_time.to_msg()
                    self.marker_pub.publish(marker)
                    marker_dict['next_time'] = current_time_in_secs + marker_dict['pub_cycle']
            # publish the persistent marker arrays 
            for key in self.marker_arrays_dict.keys():
                marker_array_dict = self.marker_arrays_dict[key]
                marker_array = marker_array_dict['marker_array'] 
                if marker_array_dict['next_time'] is None or current_time_in_secs >= marker_array_dict['next_time']:
                    marker.header.stamp = current_time.to_msg()
                    self.marker_array_pub.publish(marker_array)
                    marker_array_dict['next_time'] = current_time_in_secs + marker_array_dict['pub_cycle']                
                  
    def _cb_timer_cloud_viz(self):
        """ internal callback function 
        :meta private:
        """
        with self.lock:   
            if self.to_delete_all_pointclouds:
                self.to_delete_all_pointclouds = False
                # publish the empty pointcloud to clear 
                empty_pointcloud = create_empty_pointcloud()
                empty_pointcloud.header.frame_id = 'map'
                empty_pointcloud.header.stamp = self._node.get_clock().now().to_msg()
                self.cloud_pub.publish(empty_pointcloud)
                # clear the pointclouds_dict
                self.pointclouds_dict.clear()
                return

            # publish the persistent pointclouds
            for pointcloud_dict in self.pointclouds_dict.values():
                pointcloud = pointcloud_dict['pointcloud']
                current_time = self._node.get_clock().now().nanoseconds / 1e9
                if pointcloud_dict['next_time'] is None or current_time >= pointcloud_dict['next_time']:
                    pointcloud.header.stamp = self._node.get_clock().now().to_msg()
                    self.cloud_pub.publish(pointcloud)
                    pointcloud_dict['next_time']  = current_time + pointcloud_dict['pub_period']

    def _cb_timer_tf(self):
        """ internal callback function 
        :meta private:
        """
        with self.lock:   
            for custom_tf in self.tfs_dict.values():
                name, parent_frame, pose = custom_tf['frame'], custom_tf['parent_frame'], custom_tf['pose']
                # xyzq = pose_to_xyzq(pose)
                # self.tf_pub.sendTransform(xyzq[:3], xyzq[3:], self._node.get_clock().now().to_msg(), name, parent_frame)  
                # pose if of type Pose    
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

    def pub_marker(self, marker:Marker, pub_cycle:float=None, pub_tf:bool=False) -> Marker:
        """ Add a persistent marker

        :param marker: A marker to be persistently published
        :param pub_cycle: The rate of publishing, default None if same as the global pub cycle
        :param pub_tf: if True, the pose of the marker is published as a tf frame
        :return: The mrker
        """
        assert marker is not None, 'RvizVisualizer (add_persistent_marker): Parameter (marker) cannot be None'
        with self.lock:
            pub_cycle = 0 if pub_cycle is None else pub_cycle
            self.markers_dict[marker.ns, marker.id] = {'marker': marker, 'pub_cycle': pub_cycle, 'next_time': None, 'pub_tf': pub_tf}
            if pub_tf:
                # self.add_custom_tf(f'{marker.ns}.{marker.id}', marker.header.frame_id, marker.pose)
                self.pub_custom_tf(f'{marker.ns}.{marker.id}', marker.header.frame_id, marker.pose)
            return marker
            
    def pub_marker_once(self, marker:Marker, delay:float=0.0) -> Marker:
        """ Add an once-only marker, which is to be published only once

        :param marker: A marker to be published only once
        :param delay: The delay     
        :return: The marker
        """
        assert marker is not None, 'RvizVisualizer (pub_temporary_marker): Parameter (marker) cannot be None'
        with self.lock:
            self.once_marker_list.append({'marker': marker, 'pub_time': self._get_ros_time_in_seconds(delay)})      
            return marker 

    def pub_marker_array(self, name:str, marker_array:MarkerArray, pub_cycle:float=None) -> None:
        """ Add a marker array

        :param marker_array: A marker array to be persistently published
        :param pub_cycle: The rate of publishing, default None if same as the global pub cycle
        :param pub_tf: if True, the pose of the marker is published as a tf frame
        :return: The index of the marker array
        """
        assert marker_array is not None, 'RvizVisualizer (add_persistent_marker_array): Parameter (marker_array) cannot be None'
        with self.lock:
            pub_cycle = 0 if pub_cycle is None else pub_cycle
            self.marker_arrays_dict[name] = {'marker_array': marker_array, 'pub_cycle': pub_cycle, 'next_time': None}
        
    def pub_custom_tf(self, name:str, parent_frame:str, pose:Pose) -> None:
        """ Add a custom transform to the rviz visualizer, which is broadcast regularly

        :param name: the name of the transform
        :param xyz: the xyz pose
        :param rpy: the rpy pose
        :param frame: the reference frame
        """
        if name is None or parent_frame is None or pose is None:
            raise AssertionError(f'RvizVisualizer (add_custom_tf): No parameter can be None')
        self.tfs_dict[name] = {'pose': pose, 'frame':name, 'parent_frame': parent_frame}       
        
    def delete_all_persistent_markers(self) -> None:
        """ Remove all persistent markers from RViz and this object

        """
        with self.lock:
            # remove the tf associated with markers with pub_tf True
            for marker_dict in self.markers_dict.values():
                if marker_dict['pub_tf']:
                    marker:Marker = marker_dict['marker']
                    self.once_marker_list.append({'marker': create_delete_marker(marker.ns, marker.id), 
                                                  'pub_time': self._get_ros_time_in_seconds()}) 
                    tf_frame = f'{marker.ns}.{marker.id}'
                    if tf_frame in self.tfs_dict:
                        del self.tfs_dict[tf_frame]
            self.markers_dict.clear()

            
    def delete_marker(self, name:str, id:int) -> None:
        """ Remove a marker from RViz and this object

        :param name: the name space of the marker
        :param id: the id of the marker
        :param frame: the reference frame
        """
        assert name is not None and id is not None, \
            'RvizVisualizer (delete_marker): Parameter (any) cannot be None'
        with self.lock:
            if (name, id) in self.markers_dict:
                del self.markers_dict[name, id]
                self.pub_marker_once(create_delete_marker(name, id))
                tf_frame = f'{name}.{id}'
                if tf_frame in self.tfs_dict:
                    del self.tfs_dict[tf_frame]

    def delete_marker_array(self, name:str) -> None:
        """ Remove a persistent marker from RViz and this object

        :param name: the name space of the marker
        :param id: the id of the marker
        :param frame: the reference frame
        """
        assert name is not None, \
            'RvizVisualizer (delete_marker_array): Parameter (name) cannot be None'
        with self.lock:
            if name in self.marker_arrays_dict:
                marker_array:MarkerArray = self.marker_arrays_dict[name]['marker_array']
                del self.marker_arrays_dict[name]
                self.pub_marker_once(cre)


            if 0 <= index < len(self.marker_arrays_dict):
                marker_array:MarkerArray = self.marker_arrays_dict[index]['marker_array']
                self.marker_arrays_dict.pop(index)
                self.once_marker_list.append({'marker': create_delete_all_marker(), 
                                               'pub_time': None}) 
                return marker_array
            return None

    def delete_all_markers(self):
        """ Remove all markers from RViz

        """
        self.pub_marker_once(create_delete_all_marker())
        self.markers_dict.clear()

    def delete_all_marker_arrays(self):
        """ Remove all marker arrays from RViz

        """
        self.pub_marker_once(create_delete_all_marker_array())
        self.marker_arrays_dict.clear()

    def delete_all_pointclouds(self):
        """ Remove all pointclouds from RViz

        """
        self.to_delete_all_pointclouds = True
        self.pointclouds_dict.clear()
    
    def delete_all_in_rviz(self):
        self.delete_all_markers()
        self.delete_all_marker_arrays()
        self.delete_all_pointclouds()

    def pub_pointcloud(self, name:str, pointcloud:PointCloud2, pub_period:float=None) -> PointCloud2:
        """ Add a PointCloud2 object for regular publishing

        :param name: the name of the pointcloud of type str
        :param pointcloud: an object to be published
        :param pub_period: The rate of publishing, which cannot be smaller than 0.1 seconds
        :return: the point cloud input parameter 
        """
        with self.lock:
            pub_period = self.default_pub_cloud_cycle if pub_period is None else pub_period
            pub_period = 0.1 if pub_period < 0.1 else pub_period
            self.pointclouds_dict[name] = {'pointcloud': pointcloud, 'pub_period': pub_period, 'next_time': None}
            return pointcloud

    def delete_pointcloud(self, name:str) -> PointCloud2:
        """ Remove a pointcloud from regular publishing

        :param name: the name of the pointcloud of type str
        :return: the PointCloud2 object removed
        """
        with self.lock:
            if name in self.pointclouds_dict:
                pointcloud = self.pointclouds_dict[name]  
                del self.pointclouds_dict[name]        
                return pointcloud
            return None




