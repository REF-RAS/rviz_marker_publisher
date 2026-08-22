# Copyright 2025 - Andrew Kwok Fai LUI
# Robotics and Autonomous Systems Group, REF, RI
# Queensland University of Technology

"""A supporting module for rviz_marker_publisher."""

__author__ = "Andrew Lui"
__copyright__ = "Copyright 2025"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "ak.lui@qut.edu.au"
__status__ = "Development"

import logging
import os
import time

import pandas as pd

LOGLEVEL_VARNAME = "GLOBAL_LOGLEVEL"
LOGFILE_VARNAME = "GLOBAL_LOGFILE"
DEFAULT_LOGGER_NAME = 'rviz_marker_publisher'

# -- The custom logger for the task trees package
class CustomFormatter(logging.Formatter):
    """The custom logger class for the package.

    :meta private:
    """

    grey = "\x1b[38;20m"
    cyan = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, use_color: bool = True):
        """Initialize the CustomFormatter."""
        # input parameters
        self.use_color = use_color

        # format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'
        self.basic_format = "[%(levelname)s] [%(asctime)s.%(msecs)03d] [%(name)s]: %(message)s"
        self.color_formats = {
            logging.DEBUG: self.cyan + self.basic_format + self.reset,
            logging.INFO: self.grey + self.basic_format + self.reset,
            logging.WARNING: self.yellow + self.basic_format + self.reset,
            logging.ERROR: self.red + self.basic_format + self.reset,
            logging.CRITICAL: self.bold_red + self.basic_format + self.reset,
        }

    def format(self, record):
        """Override the method in the parent class."""
        time_format = "%Y-%m-%d %H:%M:%S"
        if self.use_color:
            log_fmt = self.color_formats.get(record.levelno)
        else:
            log_fmt = self.basic_format
        formatter = logging.Formatter(log_fmt, datefmt=time_format)
        return formatter.format(record)

    def formatException(self, exc_info):
        """Override the method in the parent class."""
        result = super().formatException(exc_info)
        return repr(result)

# create a new logger or return an existing logger given the name
def get_logger(
    name=DEFAULT_LOGGER_NAME, level: int = logging.INFO, silent: bool = False, logging_file: str | None = None, logging_file_level: int | None = None
) -> logging.Logger:
    """Create or get an existing logger givne the name and optionally the level, slient mode, and whether the log is written to a file.

    :param name: the name of the logger, defaults to DEFAULT_LOGGER_NAME
    :type name: str, optional
    :param level: the logging level, defaults to logging.INFO
    :type level: int, optional
    :param silent: if True, no display on the screen, defaults to False
    :type silent: bool, optional
    :param logging_file: if provided, the log messages are also written to a log file given in this parameter, defaults to None
    :type logging_file: str, optional
    :param logging_file_level: the logging level of messages to be written to a log file, defaults to None
    :type logging_file_level: int, optional
    :return: an instance of the logger
    :rtype: logging.Logger
    """
    # get environment variable FF3DR_LOGLEVEL
    level = os.environ.get(LOGLEVEL_VARNAME, level)
    logging_file = os.environ.get(LOGFILE_VARNAME, logging_file)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    if not logger.handlers:
        if not silent or logging_file is None:
            ch = logging.StreamHandler()
            ch.setFormatter(CustomFormatter())
            ch.setLevel(level)
            logger.addHandler(ch)
        if logging_file:
            logging_file_level = level if logging_file_level is None else logging_file_level
            fh = logging.FileHandler(logging_file)
            fh.setFormatter(CustomFormatter(use_color=False))
            fh.setLevel(logging_file_level)
            logger.addHandler(fh)
    return logger


class TimeLogger:
    """Log the amount of time taken in a profiling task."""

    def __init__(self):
        """Initialize the time logger."""
        self.start_time = time.time()
        self.logged_time_list = []
        self.logged_time_dict = {}
        self.logged_time_names_list = []

    def take(self, name: str):
        """Take the time.

        :param name: the name attached to the timestamp
        :type name: str
        """
        time_lapsed = time.time() - self.start_time
        self.logged_time_list.append((name, time_lapsed))
        self.logged_time_dict[name] = time_lapsed
        self.logged_time_names_list.append(name)

    def get_time_since_start(self) -> float:
        """Return the time since the start.

        :return: the time since the start in seconds
        :rtype: float
        """
        return time.time() - self.start_time

    def append_results_to_csv(self, id: str, csv_file: str) -> None:
        """APpend the timing results to the end of the csv file.

        :param id: The id to be added
        :type id: str
        :param csv_file: the csv file where the results are stored
        :type csv_file: str
        """
        try:
            data_df: pd.DataFrame = pd.read_csv(csv_file, index_col=False)
        except OSError:
            data_df = None

        if data_df is None:
            columns = list(self.logged_time_names_list)
            columns.insert(0, "ID")
            data_df = pd.DataFrame(columns=columns)
        self.logged_time_dict["ID"] = id
        data_df.loc[len(data_df)] = self.logged_time_dict
        # save the updated csv
        try:
            data_df.to_csv(csv_file, index=False)
            # print(f'saved timing file to {csv_file}')
        except OSError:
            print(f"failed to write to csv: {csv_file}")


# the global object to be imported by other modules
logger = get_logger()

if __name__ == "__main__":
    # print messages to remind developers of the environment variables
    logger.info("-----------------------------------------------------------------------------------------------------------------------------------------")
    logger.info(f"(logging tool) starts logging for a new process (pid: {os.getpid()}) ")
    logger.info(f"(logging tool) environment variable {LOGLEVEL_VARNAME}: {os.environ.get(LOGLEVEL_VARNAME, '')}")
    logger.info(f"(logging tool) environment variable {LOGFILE_VARNAME}: {os.environ.get(LOGFILE_VARNAME, '')}")
