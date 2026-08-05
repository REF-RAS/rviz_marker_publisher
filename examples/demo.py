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

import traceback
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rviz_marker.rviz_tools import *
from rviz_marker.logging_tools import get_logger

logger = get_logger('test_rv_node')
# -- the test program
def main():
    try:
        rclpy.init()
        the_node = Node(node_name='test_rv_node')   
        # test the mark visualization
        rv = RvizVisualizer(the_node)
        rv.spin(spin_in_thread=True)

        # start the demo
        the_pose:Pose = Pose()
        the_pose.position = Point(x=0, y=0, z=0)
        the_pose.orientation = Quaternion(x=0, y=0, z=0, q=1)
        # create world frame
        rv.add_custom_tf('world', 'map', the_pose)

        text_marker_1 = rv.add_persistent_marker(create_text_marker(name='text', id=1, text='Hello', xyzrpy=[0, 0, 0, 0.2, 0, 0], reference_frame='world', scale=0.3), pub_tf=True)
        text_marker_2 = rv.add_persistent_marker(create_text_marker(name='text', id=2, text='World', xyzrpy=[0, 1, 0, 0.2, 0, 0], reference_frame='world', scale=0.3), pub_tf=True)
        rv.add_persistent_marker(create_line_marker('line', 1, [1, 0, 0], [0, 0, 1], 'world', 0.01, rgba=[0.0, 1.0, 1.0, 1.0]), pub_period=0.1)
        rv.add_persistent_marker(create_sphere_marker('sphere', 1, [1, 1, 1], 'world', 0.05, rgba=[0.5, 1.0, 1.0, 1.0]))    
        rv.pub_temporary_marker(create_arrow_marker('arrow', 1, [1.0, 0.0, 0.0, 1.0, 0.0, 0.0], 'world', lifetime=Duration(seconds=3.0)))
        # delete the line marker
        the_node.get_clock().sleep_for(Duration(seconds=2, nanoseconds=0))
        rv.delete_persistent_marker('line', 1)
        # delete all markers
        the_node.get_clock().sleep_for(Duration(seconds=2, nanoseconds=0))
        rv.delete_all_persistent_markers()
        # display stl mesh file
        teapot_mesh = os.path.join(os.path.dirname(__file__), '../docs/assets/UtahTeapot.stl')
        teapot_mesh = 'file://' + teapot_mesh
        rv.add_persistent_marker(create_mesh_marker('teapot', 1, teapot_mesh, [-1.0, -1.0, 0.0, 0, 0, 0], 'world', [0.05, 0.05, 0.05], rgba=[0.5, 1.0, 1.0, 1.0]))  
        # display image as pointcloud
        image_bgr = cv2.imread(os.path.join(os.path.dirname(__file__), '../docs/assets/CoralFish.png'))
        pc2_message = create_pointcloud_from_image(image_bgr, (0, 0.5, 0), pixel_physical_size=[0.002, 0.002, -1], reference_frame='world')
        rv.add_pointcloud('the_image', pc2_message)
        # add the text marker
        the_node.get_clock().sleep_for(Duration(seconds=2, nanoseconds=0))
        text_marker_1 = rv.add_persistent_marker(create_text_marker('text', 1, 'Hello', [0, 0, 0, 0.2, 0, 0], 'world', 0.3), pub_period=0.1, pub_tf=True)
        for i in range(100):
            pose = text_marker_1.pose
            pose.position.x += random.uniform(-0.5, 0.5)
            the_node.get_clock().sleep_for(Duration(seconds=2, nanoseconds=0))
        # delete the text marker again
        rv.delete_persistent_marker('text', 1)
        # create marker array
        marker_array = MarkerArray()
        for x in range(4):
            for y in range(4):
                xyzrpy=[x * 0.4, y * 0.4, 1.0, 0, 0, 0]
                tile = create_cube_marker_from_xyzrpy('tile', x + y * 4, xyzrpy, reference_frame='world', 
                                        scale=[0.3, 0.3, 0.05], rgba=[0.0, 0.2, 1.0, 0.5])
                marker_array.markers.append(tile)    
        rv.add_persistent_marker_array(marker_array)
        the_node.get_clock().sleep_for(Duration(seconds=5, nanoseconds=0))
        rv.delete_all_persistent_marker_arrays()
        logger.info(f'The demo is completed')
        input('Press Enter to terminate')
        rclpy.shutdown()
    except:
        traceback.print_exc()

if __name__ == '__main__':
    main()