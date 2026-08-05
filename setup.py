import os, glob, sys
from setuptools import find_packages, setup
from ament_index_python import get_packages_with_prefixes, get_package_share_directory

package_name = 'rviz_marker_tools_ros2'

# colcon build --packages-select rviz_marker_tools_ros2 --event-handlers console_direct+ 
# colcon build --symlink-install --packages-select rviz_marker_tools_ros2 --event-handlers console_stderr+
# colcon build --symlink-install

def find_console_scripts(folders_list):
    # parent_folder = get_package_share_directory(package_name)
    if isinstance(folders_list, str):
        folders_list = [folders_list]
    scripts = []
    for folder in folders_list:
        # Walk through the directory and subfolders
        for root, dirs, files in os.walk(folder):
            for file in files:
                # Check for python files, excluding __init__.py
                if file.endswith('.py') and file != '__init__.py':
                    # buid the module path in the format my_package.subfolder.script
                    rel_path = os.path.relpath(os.path.join(root, file), '.')
                    module_path = rel_path.replace(os.path.sep, '.')[:-3]
                    # create a command name 'command_name = module.path:main_function'
                    # script_name = file[:-3].replace('_', '-')
                    script_name = file[:-3]
                    scripts.append(f'{script_name} = {module_path}:main')
    return scripts

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob.glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'config'), glob.glob(os.path.join('config', '*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Andrew Lui',
    maintainer_email='luia2@qut.edu.au',
    description='The arm commander ROS2 implementation',
    license='BSD-3',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': find_console_scripts(['examples']),
        # 'console_scripts': 'display_info = examples.move.display_info:main',
    },
)
