#!/usr/bin/python
"""This module contains classes for interacting with the DSR MMI interface.The
purpose of this module is to provide predefined MMI calls to simplify code in
functions used by the MORTAR test framework. Most methods contained in this the
module will return a "_functor" dictionary, which is expected by MORTAR. 
"""
__version__ = '0.1'
__author__ = 'Steve Ybarra'

from pprint import pprint
from ast import literal_eval
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages import urllib3 

import json
import yaml
import os
import logging
import requests
import inspect
import re
import datetime
import socket
from logging.config import fileConfig
fileConfig('logging_config.ini')
logger = logging.getLogger()
#########################################
# CLASS: MMI
#########################################


class MMI(object):
    """    
    This class defines methods for use in retrieving/updating data from the 
    active NOAMP via the MMI interface.

    Attributes: 
    ip      : (string) IP address or hostname of the target DSR.
    pathfile: (string) Name of yaml file containing a dictionary list of paths.
    """

    def __init__(self, ip=None):
        self.ip = ip
        if self.ip is not None:
            ipRegex = re.compile(r'(([01]?[0-9]?[0-9]|2[0-4][0-9]|2[5][0-5])\.){3}([01]?[0-9]?[0-9]|2[0-4][0-9]|2[5][0-5])')
            if re.match(ipRegex, self.ip) is None:
                self.ip_from_host=socket.gethostbyname(self.ip)
                if re.match(ipRegex,self.ip_from_host) is None:
                    raise ValueError('IP Address Invalid')

            self.pathfile = dict()
	    try:
	        with open(ip+'.txt') as json_data:
		    logger.info("Found " + ip +".txt")
                    d=json.load(json_data)
		    f=self.validate_token(d)
                    if f:
		        self.authToken = self.GetAuthToken()
		    else:
                        self.authToken=d["data"]["token"]
	    except Exception as e:
		print(str(e))
                self.authToken = self.GetAuthToken()
        #requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        urllib3.disable_warnings()

    def validate_token(self,d):
	logger.info("Validating token")
        m=re.search('[0-9]{4}\-[0-9]{2}\-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}',d["data"]["gooduntil"])
        validity=m.group(0)
        valid=re.sub('[T:-]','',m.group(0))
        now_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        if now_time > valid:
                logger.info("Invalid")
                return 1
        else:
                print "valid time"
                return 0

    def GetBaseUrl(self):
        """
        Build the base url given an IP.
        return completeUrl: (string) The base url value.
        """
        # TODO: Versions requires only "{scheme}://{netloc}/mmi" be used. 
        # This function should be expanded to handle Versions.
        completeUrl = "{scheme}://{netloc}/mmi/{app}/{ver}".format(
            scheme = "https",
            netloc = self.ip,
            app    = "dsr",
            ver    = "v1.0"
        )  
        return completeUrl
       
    def GetAuthToken(self):
        """
        :return: (string) API authToken. 
        """
        #print("Inside getAuthToken")
        ip = self.ip
        url = "{}/auth/tokens".format(self.GetBaseUrl())
        credentials = {"username":"guiadmin", "password":"tekware"}
        r = requests.post(url, verify=False, data=credentials)
        f=open(ip+'.txt','w')
	f.write(r.text)
	f.close()
        return r.json()['data']['token']
    

    def GetUpdateToken(self, url):
        """
        DEPRECATED
        Retrieve the update token for a given resource provided the IP and 
        resource name.
        :param url: (str) Specific path to be added to the base url or complete 
        url.
        :return: (str) update token 
        """
        if not url.startswith("https"):
            ip = self.ip
            url = "{baseUrl}/{specPath}".format(
                baseUrl  = self.GetBaseUrl(), 
                specPath = url 
            )

        #print("[+] Update token request to :" + url)
        headers = {"X-Auth-Token" : self.authToken}
        r = requests.get(url, verify=False, headers=headers)
        if "_updatetoken" in r.json()["data"]:
            return r.json()["data"]["_updatetoken"]
        else:
            print("[-] Failed to get updated token for {}.".format(url))
            return


    def GetDsr(self, specPath, payload=None):
        """
        Retrieves the contents of a given resource at specPath.
        :param specPath: (string) Specific path to be added to the base url.
            Ex. "topo/servers"
                "topo/servergroups"

        :param payload: (dict) query parameters.
        :returns (requests.models.Response).
        """
        ip = self.ip
        url = "{baseUrl}/{specPath}".format(
            baseUrl  = self.GetBaseUrl(), 
            specPath = specPath
        )
        headers={"X-Auth-Token" : self.authToken}
        response = requests.get(url, verify=False, headers=headers,
                params=payload)
	logger.info("[+] GET {} @{}".format(response.status_code, response.url))

        #print("[+] GET {} @{}".format(response.status_code, response.url))
        #print("[+] Elapsed : {}".format(response.elapsed))
        #print("[+] Response.. {}".format(response.json().get("messages"))) 
        return response  


    def PostDsr(self, specPath, data):
        """
        This method sends and http post command to the DSR MMI interface for the
        a given resource (defined in specPath).
        The post command is equal to the GUI insert command.
        :param specPath: (string) Specific path to be added to the base url.
            Ex. "topo/servers"
                "topo/servergroups"
        :param data: (dict) data to be sent to the target server.
        :returns (requests.models.Response).
        """
        #print("Inside PostDsr")
        ip = self.ip
        #print("ip and path and data %s,%s,%s",ip,specPath,data)
        url = "{baseUrl}/{specPath}".format(
            baseUrl  = self.GetBaseUrl(), 
            specPath = specPath
        )
        
        headers={"X-Auth-Token" : self.authToken}
        #print("After authToken")
        #print("url link %s", url)
        #print("Header indo %s", headers)  
        #data_tmp=json.dumps(data)
        #data = data.replace('false','False')
        #print "AFTER ---->",data
        #post = requests.post(url, verify=False, data=json.dumps(data),
            #headers=headers)
        post = requests.post(url, verify=False, data=data, headers=headers)
        #print("Post Done")
        logger.info("[+] POST {} @{}".format(post.status_code, post.url))
        return post


    def PutDsr(self, specPath, data):
        """
        This method sends and http put command to the DSR MMI interface for a 
        given resource (defined in specPath). Put is equal to GUI Edit.
        :param specPath: (string) Specific path to be added to the base url.
            Ex. "topo/servers"
                "topo/servergroups"
        :param data: (dict) data to be sent to the target server and is passed 
        with the updated token added to it.
        :returns (requests.models.Response).
        """
        ip = self.ip
        url = "{baseUrl}/{specPath}".format(
            baseUrl  = self.GetBaseUrl(), 
            specPath = specPath
        )
        headers={"X-Auth-Token" : self.authToken}
        put = requests.put(url, data=json.dumps(data), verify=False,
            headers=headers)
        ##print(put.text)
        logger.info("[+] PUT {} @{}".format(put.status_code, put.url))
        #print("[+] Elapsed : {}".format(put.elapsed))
        return put


    def DeleteDsr(self, specPath, recData):
        """
        This method sends a delete command to the DSR MMI interface for a given 
        resource (defined in specPath).
        :param specPath: (string) Specific path to be added to the base url.
            Ex. "topo/servers"
            "topo/servergroups"
        :param recData: (list) contains [<id/name>, val] and is passed with the 
        updated token added to it.
        :returns (requests.models.Response).
        """
        ip = self.ip
        print(recData)
        url = "{baseUrl}/{specPath}/{recordName}".format(
            baseUrl      = self.GetBaseUrl(), 
            specPath     = specPath,
            recordName   = recData
        )
        #upToken = self.GetUpdateToken(url)
        data = {
           #"_updatetoken" : upToken,
               #recData[0]     : recData[1]
        }
        headers={"X-Auth-Token" : self.authToken}
        delete = requests.delete(url, data=json.dumps(data), verify=False, 
            headers=headers)

        logger.info("[+] DELETE {} @{}".format(delete.status_code, delete.url))
        #print("[+] Elapsed : {}".format(delete.elapsed))
        return delete


    #Read and write files
    def ReadMmi(self, inputfile):
        """
        Read a given json file into a python dictionary
        :param inputfile: (str) name of json or yaml file to read.
        :return (dict/list) returns dict or list of dicts depending the contents
        of the input file.
        """
        #Read JSON file.
        if inputfile.endswith(".json"):
            with open(inputfile, "r") as datafile:
                try:
                    jsondict = json.load(datafile)
                    return jsondict

                except json.JSONError as jsonerr:
                    print(jsonerr)
       
        #Read yaml file
        elif inputfile.endswith(".yml"):
            with open(inputfile, "r") as datafile:
                try:
                    ymldict = yaml.load(datafile)
                    return ymldict

                except yaml.YAMLError as ymlerr:
                    print(ymlerr)


    def WriteMmi(self, data, fileName, specPath=None, clobber=True):
        """
        Write a JSON or YAML file from a python dictionary. If YAML formated
        file is desired fileName must have the ".yml" extention.
        :param data: (list) list of dictionary formated data records.  
        :param filename: (str) Desired filename
        :param specPath: (str) Path to specific resource.
        :param clobber: (bool) If True the specficed file will be overwritten. 
        If False, data will be appended to specifed file. (Default=True)
        """
        if clobber == True: 
            writetype = "w"
        else: 
            writetype = "a"

        #Add specPath identifier to data records.
        for record in data:
            if specPath != None:
                record["specPath"] = specPath

        #write YAML file
        print ("Inside writeMmi function")
        if fileName.endswith(".yml"):
            try:
                print "Inside YML"
                with open(fileName, writetype) as yamlFile:
                    yaml.safe_dump(data, yamlFile, default_flow_style=False, 
                        allow_unicode=True)
            except Exception, e:
                print(e)

        #Write JSON file
        elif fileName.endswith(".json"):
            #fileName = fileName + ".json"
            try:
	        print "Inside JSON"
                with open(fileName, writetype) as jsonFile:
                    json.dump(data, jsonFile, indent=4, sort_keys=True,ensure_ascii=False)
            except Exception, e:
                print(e)

        else:
            try:
                print "Inside ELSE"
                with open(fileName, writetype) as jsonFile:
                    json.dump(data, jsonFile, indent=4, sort_keys=True)    
            except Exception, e:
                print(e)

    @staticmethod
    def IsFail(retVal):
        """
        Determine if return value contains as failed status code.
        """
        try:
            #Fail if no Status present
            status = retVal.get("Status")
            if status >= 300:
                fail = True
                return fail
        except:
            fail = False
            return fail


    @staticmethod
    def myname():
        """Find the name of the method from which this one is called.
        """
        return inspect.stack()[1][3]

    def IsAvailable(ip):
        """
        """


if __name__ == "__main__":
    main()   
