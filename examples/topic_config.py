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
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
from visualization_msgs.msg import Marker, MarkerArray
import rviz_marker
from rviz_marker import RvizVisualizer, get_logger
logger = get_logger()

def create_grid_marker_array(grid_dim:tuple, grid_cell_size:tuple, tile_size:tuple) -> MarkerArray:
    """ create a MarkerArray according to the grid dimension, cell size, and tile size

    :param grid_dim: the grid dimension (nx, ny)
    :type grid_dim: tuple
    :param grid_cell_size: the size of each cell (dx, dy)
    :type grid_cell_size: tuple
    :param tile_size: the size of each tile inside the cell (dx, dy)
    :type tile_size: tuple
    :return: the marker array
    :rtype: MarkerArray
    """
    markers_list:list[Marker] = []
    for x in range(grid_dim[0]):
        for y in range(grid_dim[1]):
            xyzrpy=[x * grid_cell_size[0], y * grid_cell_size[1], 0.0, 0, 0, 0]
            tile = rviz_marker.create_cube_marker_from_xyzrpy('tile', x + y * grid_dim[0], xyzrpy, reference_frame='map', 
                                    scale=[tile_size[0], tile_size[1], tile_size[2]], rgba=[0.0, 0.2, 1.0, 0.5],
                                    lifetime=5.0)
            markers_list.append(tile)

    marker_array = rviz_marker.create_marker_array(markers_list)
    return marker_array

def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizVisualizer(the_node)
    rviz_marker.spin_in_thread(the_node)
    # activate topics
    rv.activate_topic('/rviz_marker', Marker)
    rv.activate_topic('/rviz_marker_array', MarkerArray)
    # wait for the discovery and matching on the dds layer
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(3.0)
    # remove existing markers
    logger.info('(reset rviz) remove all in rviz and wait for 2 secs')
    rv.delete_all_objects_by_topics()
    time.sleep(2.0) 
    logger.info('(add) create_sphere_marker and publish it to the topic /rviz_marker')
    sphere_marker = rviz_marker.create_sphere_marker(name='sphere', id=1, xyz=[1, 1, 1], reference_frame='map', 
                                                scale=0.20, rgba=[1.0, 0.5, 0.5, 1.0])
    rv.publish_and_register(sphere_marker, topic='/rviz_marker')
    # add a marker array of 9x3 cubes with lifetime of 5.0 seconds
    logger.info('(add) create_marker_array of a 9x3 thin cubes with lifetime of 5 secs and publish to /rviz_marker_array')
    marker_array = create_grid_marker_array((9, 3), (0.5, 0.5), (0.46, 0.46, 0.01))
    rv.publish_best_effort_once(marker_array, topic='/rviz_marker_array')
    time.sleep(10.0)
    # delete the objects from the new topics
    logger.info('(delete) delete_objects_of_topics "/rviz_marker" and "/rviz_marker_array"')
    rv.delete_registered_objects_by_topics(['/rviz_marker', '/rviz_marker_array'])
    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()