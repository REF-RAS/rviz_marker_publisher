import os, glob, sys, subprocess
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

# from ament_index_python import get_packages_with_prefixes, get_package_share_directory

# rosdep update && rosdep install -y -r -i --rosdistro jazzy --from-paths .

# pip install -e /workspace/ros2_ws/src/rviz_marker_publisher/

# colcon build --packages-select rviz_marker_publisher --event-handlers console_direct+ 
# colcon build --symlink-install --packages-select rviz_marker_publisher --event-handlers console_direct+ 
# colcon build --symlink-install --packages-select rviz_marker_publisher --event-handlers console_stderr+
# colcon build --symlink-install --event-handlers console_direct+ 


# custom build step to force uv to run before compiling the package
class UVInstallThenBuild(build_py):
    def run(self):
        dependencies = INSTALL_REQUIRES
        print(f"(UVInstallThenBuild) Forcing dependency installation via UV: {dependencies} {__file__}")
        
        # check if uv is installed, default to pip if missing
        uv_path = subprocess.run(["which", "uv"], capture_output=True, text=True).stdout.strip()
        if uv_path:
            installer = ['uv', "pip", "install"]
            # add --system flag it is running in a docker container
            if Path('/.dockerenv').is_file():
                if self.can_run_sudo():
                    installer.insert(0, 'sudo')
                installer.append("--system")
            installer = installer + dependencies
        else:  # fallback to pip install
            installer = [sys.executable, "-m", "pip", "install"]
            if Path('/.dockerenv').is_file():
                if self.can_run_sudo():
                    print(f'CAN DO SUDO')
                    installer.insert(0, 'sudo')
                installer.append("--break-system-packages")
            installer = installer + dependencies

        subprocess.run(installer, check=True)
        super().run()
        
    def can_run_sudo(self) -> bool:
        try:
            # Run sudo validation in non-interactive mode
            result = subprocess.run(
                ["sudo", "-v", "-n"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                return True
            if "a password is required" in result.stderr.lower():
                return True
            return False
        except FileNotFoundError:
            return False

def find_console_scripts(console_script_folders_list:list[dict]):
    # parent_folder = get_package_share_directory(PACKAGE_NAME)
    if isinstance(console_script_folders_list, dict):
        console_script_folders_list = [console_script_folders_list]
    scripts = []
    for folder_spec in console_script_folders_list:
        source = folder_spec['source']
        folder_list = folder_spec.get('include', [])
        if isinstance(folder_list, str):
            folder_list = [folder_list]
        for folder in folder_list:
            # Walk through the directory and subfolders
            for root, dirs, files in os.walk(os.path.join(source, folder)):
                for file in files:
                    # Check for python files, excluding __init__.py
                    if file.endswith('.py') and file != '__init__.py':
                        # buid the module path in the format my_package.subfolder.script
                        rel_path = os.path.relpath(os.path.join(root, file), source)
                        module_path = rel_path.replace(os.path.sep, '.')[:-3]
                        # create a command name 'command_name = module.path:main_function'
                        # script_name = file[:-3].replace('_', '-')
                        script_name = file[:-3]
                        scripts.append(f'{script_name} = {module_path}:main')
    return scripts

# results = find_console_scripts([dict(source='src', include='examples')])
# print(f'find_console_scripts: {results}', file=sys.stderr)

# results = find_packages(where='src', include=['rviz_marker_publisher', 'examples'])
# print(f'find_packages: {results}', file=sys.stderr)

PACKAGE_NAME = 'rviz_marker_publisher'
INSTALL_REQUIRES = [
    'opencv_python',
    'wrapt<2.0.0',
    'numpy<=2',
    'pandas',
    'ruff',
]

setup(
    name=PACKAGE_NAME,
    version='0.1.0',
    packages=find_packages(where='src', include=['rviz_marker_publisher', 'examples']),
    package_dir={'': 'src'},
    cmdclass={
        'build_py': UVInstallThenBuild,  # inject the custom UV step
    },
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + PACKAGE_NAME]),
        ('share/' + PACKAGE_NAME, ['package.xml']),
        (os.path.join('share', PACKAGE_NAME, 'launch'), glob.glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', PACKAGE_NAME, 'config'), glob.glob(os.path.join('config', '*'))),
        (os.path.join('share', PACKAGE_NAME, 'examples', 'assets'), glob.glob(os.path.join('src', 'examples', 'assets', '*'))),
    ],
    install_requires=INSTALL_REQUIRES,
    zip_safe=True,
    maintainer='Andrew Lui',
    maintainer_email='ak.lui@qut.edu.au',
    description='The RViz Marker Tools for ROS2',
    license='NON AI BSD-3',
    extras_require={                                    # extras_require instead of tests_require in new setuptools version
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': find_console_scripts([dict(source='src', include='examples')]),
    },
)
