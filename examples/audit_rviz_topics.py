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
from sensor_msgs.msg import PointCloud2
from visualization_msgs.msg import Marker, MarkerArray
from rosidl_runtime_py.utilities import get_message
import rviz_marker
from rviz_marker import RvizVisualizer, get_logger
logger = get_logger()

def main():
    rclpy.init()
    the_node = Node(node_name='test_rv_node') 
    # create the RVizVisualizer 
    rv = RvizVisualizer(the_node)
    rviz_marker.spin_in_thread(the_node)
    # wait for the discovery and matching on the dds layer
    logger.info('(wait) discovery and matching of publishers and subscribers')
    time.sleep(3.0)
    # initialize variable
    visualization_topics = []
    # audit rviz topics
    subscriptions_dict = rv.audit_rviz_subscriptions()
    for topic, message_names_list in subscriptions_dict.items():
        for message_name in message_names_list:
            message_class = get_message(message_name)
            if message_class in (Marker, MarkerArray, PointCloud2):
                visualization_topics.append(topic)
                logger.info(f'the topic {topic} is one of the visualization types')

    # remove existing markers
    logger.info('(reset rviz) delete all objects in the rviz subscribed topics and wait for 2 secs')
    logger.info(f'(reset rviz) the subscribed topics: {visualization_topics}')
    rv.delete_all_objects_by_topics(visualization_topics)
    time.sleep(2.0)   

    # pause before terminate until Enter is press
    input('Press Enter to terminate')
    rclpy.shutdown()

if __name__ == '__main__':
    main()