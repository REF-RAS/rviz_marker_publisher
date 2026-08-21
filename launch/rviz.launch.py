import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    ros2_package_name = __package__.split('.')[0] if __package__ else 'rviz_marker_publisher'
    # Find the package share directory
    pkg_share = get_package_share_directory(ros2_package_name)
    
    # Path to the rviz config file
    rviz_config_path = os.path.join(pkg_share, 'config', 'demo.rviz')

    return LaunchDescription([
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_path],
            output='screen'
        )
    ])
