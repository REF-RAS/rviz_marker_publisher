import os, glob, sys, subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

# from ament_index_python import get_packages_with_prefixes, get_package_share_directory

# rosdep update && rosdep install -y -r -i --rosdistro jazzy --from-paths .

# pip install -e /workspace/ros2_ws/src/rviz_marker_publisher/

# colcon build --packages-select rviz_marker_publisher --event-handlers console_direct+ 
# colcon build --symlink-install --packages-select rviz_marker_publisher --event-handlers console_direct+ 
# colcon build --symlink-install --packages-select rviz_marker_publisher --event-handlers console_stderr+
# colcon build --symlink-install

PACKAGE_NAME = 'rviz_marker_publisher'
INSTALL_REQUIRES = [
    'opencv_contrib_python>=5',
    'wrapt',
    'pandas'
]
EXTRA_REQUIRES = {
    'test': ['pytest'],
}

# custom build step to force uv to run before compiling the package
class UVInstallThenBuild(build_py):
    def run(self):
        dependencies = INSTALL_REQUIRES
        print(f"(UVInstallThenBuild) Forcing dependency installation via UV: {dependencies} {__file__}")
        
        # check if uv is installed, default to pip if missing
        uv_path = subprocess.run(["which", "uv"], capture_output=True, text=True).stdout.strip()
        installer = ['sudo', 'uv', "pip", "install"] if uv_path else [sys.executable, "-m", "pip", "install"]
        
        # add --system flag if outside a virtual environment to prevent uv from blocking global installs
        if not uv_path or "VIRTUAL_ENV" not in os.environ:
            installer.append("--system")

        subprocess.run(installer + dependencies, check=True)
        super().run()

# 
def find_console_scripts(folders_list):
    # parent_folder = get_package_share_directory(PACKAGE_NAME)
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
    name=PACKAGE_NAME,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    cmdclass={
        'build_py': UVInstallThenBuild,  # inject the custom UV step
    },
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + PACKAGE_NAME]),
        ('share/' + PACKAGE_NAME, ['package.xml']),
        (os.path.join('share', PACKAGE_NAME, 'launch'), glob.glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', PACKAGE_NAME, 'config'), glob.glob(os.path.join('config', '*'))),
        (os.path.join('share', PACKAGE_NAME, 'examples', 'assets'), glob.glob(os.path.join('examples', 'assets', '*'))),
    ],
    install_requires=INSTALL_REQUIRES,
    zip_safe=True,
    maintainer='Andrew Lui',
    maintainer_email='ak.lui@qut.edu.au',
    description='The RViz Marker Tools for ROS2',
    license='NON AI BSD-3',
    extras_require=EXTRA_REQUIRES,
    entry_points={
        'console_scripts': find_console_scripts(['examples']),
        # 'console_scripts': 'display_info = examples.move.display_info:main',
    },
)
