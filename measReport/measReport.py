"""
This Python file contains the code required to collect measurement data through MMI calls.

This file can be run on its own by reading user input from configuration file.

History
---------------------------------------------------------------------
Rahul Roshan  03/03/2017   Initial creation
"""

#!/usr/bin/python
from pyMMI import MMI
from pprint import pprint
import ConfigParser
import json
import sys
import urllib


#########################################
# CLASS: Measurement_Report
#########################################
class Measurement_Report():
    """
    This class defines the methods to read the configuration file <meas_config.cfg>
    and create the URI.
    """
    def __init__(self,cfg_file):
        self.cfg_file = cfg_file
        self.query_string=self.read_cfg(self.cfg_file)

    def get_query(self):
	return self.query_string

    def read_cfg(self,cfg_file):
        """
        Create the query string based on the uswerinput from the configuration file.
        """
        configParser = ConfigParser.RawConfigParser()
        configParser.read(cfg_file)
        query_string = {}
        query_string['traceOn']    = configParser.get('data-config', 'traceOn')
        query_string['time_unit']  = configParser.get('data-config', 'time_unit')
        query_string['time_count'] = configParser.get('data-config', 'time_count')
        query_string['scope_type'] = configParser.get('data-config', 'scope_type')
        query_string['scope_name'] = configParser.get('data-config', 'scope_name')
        query_string['ids']        = configParser.get('data-config', 'ids')
        query_string['interval']   = configParser.get('data-config', 'interval')
        query_string['group']      = configParser.get('data-config', 'group')
        query_string['pattern']    = configParser.get('data-config', 'pattern')
        query_string['range']      = configParser.get('data-config', 'range')
        return query_string
