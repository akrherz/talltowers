# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 00:08:50 2016

@author: joe
"""
import os
import json

CONFIG = json.load(
    open(os.path.dirname(__file__) + "/../config/settings.json", 'r'))


class logger_configurator():
    """
    object to instantiate logger configuration dictionary.  This also
    checks/makes
    the log files, so that there are no errors when logging.config.dictConfig()
    is called.
    ...couldn't make the logging.config.dictConfig() work with just the class
    variable,
    because the files were not created when the importing log_conf.py, but as
    a Class, it is instantiated with a function that makes the log files.
    """
    # make class variables, out of the base configuration file.
    log_conf_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": ("%(asctime)s -- [%(funcName)s] -- "
                           "%(levelname)s -- %(message)s")
            },
            "errors": {
                "format": ("%(asctime)s -- [%(funcName)s   line:%(lineno)3d] "
                           "-- %(levelname)s -- %(message)s")
            }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },

            "info_file_handler": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": os.path.join(CONFIG['dataroot'], "logs",
                                         "csi2pg.log"),
                "when": "W0",    # weekly, new file on Mondays
                "backupCount": 20,
                "encoding": "utf8"
            },

            "error_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "errors",
                "filename": os.path.join(CONFIG['dataroot'], "logs",
                                         "error.log"),
                "maxBytes": 1048576,    # 1MB
                "backupCount": 20,
                "encoding": "utf8"
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "info_file_handler", "error_file_handler"]
        }
    }

    def __init__(self):
        # instantiate object
        self.ffn_error = (
            self.log_conf_dict["handlers"]["error_file_handler"]["filename"])
        self.ffn_log = (
            self.log_conf_dict["handlers"]["info_file_handler"]["filename"])

    def make_log_files(self):
        # create the paths to the files
        self.touch(self.ffn_error)
        self.touch(self.ffn_log)

    def touch(self, ffn):
        """
        Create empty file, or update its time of last access,
        and if necessicary, creat the path to that file
        """
        path = os.path.dirname(ffn)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(ffn, 'a'):
            os.utime(ffn, None)
