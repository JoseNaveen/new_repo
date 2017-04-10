#!/usr/bin/python
from class_from_schema import *
import unittest
import get_report
import findServer
import modify_ngnps
import modify_drmp
from pyMMI import *
import sys
import json
import xml.etree.ElementTree as ET
from shellcommand import *
import time
import logging
from time import sleep
from logging.config import fileConfig
client_connection="ClientConnection"
from measReport import *
from get_report import *
###Seagull filenames
client_config="DRMP_CLI_CONF_001.xml"
client_scenario="clients/DRMP_CLI_SCEN_001.xml"
server_config="DRMP_SRV_CONF_01.xml"
server_scenario="servers/DRMP_SRV_SCEN_01.xml"

CLIENTCOMMAND1 = "seagull -bg -conf clients/DRMP_CLI_CONF_001.xml -dico clients/DRMP_CLI_DCT.xml -scen clients/DRMP_CLI_SCEN_001.xml -log Client.log -llevel ETU &> /dev/null"

SERVERCOMMAND1 = "seagull -bg -conf servers/DRMP_SRV_CONF_01.xml -dico servers/DRMP_SRV_DCT.xml -scen servers/DRMP_SRV_SCEN_01.xml -log Server.log -llevel ETU &> /dev/null"

#SERVERCOMMAND = "seagull -bg -conf servers/Rambler_MED_RBAR_SERVER_CONF.xml -dico servers/Server_Dictionary.xml -scen servers/Rambler_RBAR_MED_SERVER_SCEN.xml -log server.log -llevel ETU &> /dev/null"

#CLIENTCOMMAND = "seagull -bg -conf clients/Rambler_MED_RBAR_CLIENT_CONF.xml -dico clients/Client_Dictionary.xml -scen clients/Rambler_RBAR_MED_CLIENT_SCEN.xml -log Client.log -llevel ETU &> /dev/null"


server_connection="DRMP_Server_Conn001"
server_connection="ServerConnection"
CALL_RATE=10
#Run time in seconds
RUN_TIME=360


fileConfig('logging_config.ini')
logger = logging.getLogger()


class DRMP_Test1():
    def __init__(self,ip=None):
        self.dsr=MMI(ip)
        self.soamobj,self.soam=findServer.getActiveSOAM(self.dsr)
        self.servers=self.dsr.GetDsr('topo/servers')
        self.sgs=self.dsr.GetDsr('topo/servergroups')
        self.MPSG=[i['name'] for i in self.sgs.json()['data'] if i['functionName']=="DSR (multi-active cluster)"]

    def enable_connection(self,conn_name):
	self.enable={}
	self.enable["adminState"]="Enabled"
        logger.info("Enabling Connection %s ",conn_name)
	self.response=self.soamobj.PutDsr("diameter/connections/" + conn_name +"/connectionadminstate",self.enable)
        return self.response

    def disable_connection(self,conn_name):
        self.disable={}
        self.disable["adminState"]="Disabled"
        logger.info("Disable Connection %s ",conn_name)
        self.response=self.soamobj.PutDsr("diameter/connections/" + conn_name +"/connectionadminstate",self.disable)
	return self.response
    def check_connection_status(self,conn_name):
        self.response=self.soamobj.GetDsr("diameter/connections/" + conn_name +"/status")
        try: 
	    if self.response.json()["data"]["operationalStatus"] == "Available":
		return 1
	    else:
		return 0
	except:
	    return 0
    def add_capacity_config_set(self,data):
        self.r=self.soamobj.PostDsr('diameter/capacityconfigurationsets',data.serialize())
        return 1
    def delete_capacity_config_set(self,data):
        self.r=self.soamobj.DeleteDsr('diameter/capacityconfigurationsets',data)
	return 1
    def add_peernode(self,data):
        self.r=self.soamobj.PostDsr('diameter/peernodes',data.serialize())
        return 1
    def delete_peernode(self,data):
        self.r=self.soamobj.DeleteDsr('diameter/peernodes' , data['name'])
	return 1
    def delete_connection(self,data):
        self.r=self.soamobj.DeleteDsr('diameter/connections' , data['name'])
	return 1
    def add_connection(self,data):
        self.r=self.soamobj.PostDsr('diameter/connections',data.serialize())
        return 1
    def restart_mps(self):
        """
        for i in self.sgs.json()['data']:
            if i['functionName']=="DSR (multi-active cluster)":
                self.MPSG=i['name']
        """
        self.sinsg={k:[] for k in self.MPSG}
        #[self.singsg[i['serverGroupName'].append(i['hostname']) for i in self.servers.json()['data'] if i['serverGroupName'] in self.MPSG]
        for i in self.servers.json()['data']:
            if i['serverGroupName'] in self.MPSG:
                self.sinsg[i['serverGroupName']].append(i['hostname'])
        self.data_enabled={}
        self.data_disabled={}
        self.data_enabled['applState']="Enabled"
        self.data_disabled['applState']="Disabled"
        for k in self.sinsg:
            for i in self.sinsg[k]:
	        logger.info("Disabling application on %s",i)
                self.dsr.PutDsr('topo/servers/' + i + '/appl',self.data_disabled)
                time.sleep(15)
		logger.info("Enabling application on %s",i)
                self.dsr.PutDsr('topo/servers/' + i + '/appl',self.data_enabled)
		time.sleep(15)
            
    def enable_drmp(self):
        logger.info("Enabling DRMP")
        modify_drmp.enable_drmp(self.soam)
        self.restart_mps()        
    def disable_drmp(self):
        logger.info("Disabling DRMP")
        modify_drmp.disable_drmp(self.soam)
	self.restart_mps()
    def enable_ngnps(self):
        logger.info("Enable NGNPS")
        modify_ngnps.enable_ngnps(self.soam)
	self.restart_mps()
    def disable_ngnps(self):
        logger.info("Disable NGNPS")
        modify_ngnps.disable_ngnps(self.soam)
	self.restart_mps()
     


def read_config():
    yaml_config=open('config.yaml')
    config=yaml.load(yaml_config)
    yaml_config.close()
    return config


def set_priority(scenario_path,priority):
    tree=ET.parse(scenario_path)
    for elem in tree.iterfind('traffic/send/command/avp[@name="DRMP"]'):
        elem.set('value',str(priority))
        print(elem.tag,elem.attrib)
    tree.write(scenario_path)


def start_traffic(connection):
    Traffic=ShellCommand(connection,0)
    
def run_test(client,server,testcase):
    start_traffic(SERVERCOMMAND1)
    t_end=time.time() + 50
    while testcase.check_connection_status(server_connection)!=1:
        if time.time() > t_end:
            print("Connection Failed to come up")
            return 0
            break
        sleep(3)
    start_traffic(CLIENTCOMMAND1)
    t_end=time.time() + 30
    while testcase.check_connection_status(client_connection)!=1:
        if time.time() > t_end:
            print("Connection Failed to come up")
            return 0
            break
        sleep(3)
    logger.info("Running Traffic")
    sleep(120)
    return 1


def collect_counters(dsr,pegcounter):
    d=open('meas_ids.txt')
    counter_filter={}
    counter_filter['scope_name']=dsr.MPSG[0]
    counter_filter['scope_type']="ServerGroup"
    counter_filter['time_count']="-5"
    for i in d:
        k,v=i.strip().split(' ')
        if v==pegcounter:
            meas_id=k
            break
    counter_filter['ids']=meas_id
    counter_filter['client']=dsr.soamobj
    resp=get_report.mmi_get_counter(**counter_filter)
    return int(resp.json()['data']['servers'][0]['metrics'][0]['timestampValues'][0]['values'][0])

def clean_dsr(**args):
    for k,v in args.iteritems():
        if k=='connection':
	    for i in v:
		logger.info("Disabling connection %s",i['name'])
	        args['test'].disable_connection(i['name'])
		sleep(3)
		logger.info("Deleting connection %s",i['name'])
		args['test'].delete_connection(i)
    for k,v in args.iteritems():
	if k=='peernode':
	    for i in v:
	        logger.info("Deleting Peernode %s",i['name'])
	        args['test'].delete_peernode(i)
    for k,v in args.iteritems():		
	if k=='capacity_config_set':
	    for i in v:
	        logger.info("Deleting Capacity Config Set %s",i)
	        args['test'].delete_capacity_config_set(i)
    

def main(*args):
    testcase=DRMP_Test1(*args)
    logger.info("Starting test")
    config=read_config()
    for i in config['DRMP1']['DSRCONFIG']['SYSTEMOPTIONS']:
        if i=='16PAdminState':
            if config['DRMP1']['DSRCONFIG']['SYSTEMOPTIONS']['16PAdminState']=="enabled":
	        logger.info("Enabling DRMP")
                testcase.enable_drmp()
            if config['DRMP1']['DSRCONFIG']['SYSTEMOPTIONS']['16PAdminState']=="disabled":
	        logger.info("Disabling DRMP")
                testcase.disable_drmp()
        if i=='NgnPsAdminState':
            if config['DRMP1']['DSRCONFIG']['SYSTEMOPTIONS']['NgnPsAdminState']=="enabled":
	        logger.info("Enabling NGNPS")
                testcase.enable_ngnps()
            if config['DRMP1']['DSRCONFIG']['SYSTEMOPTIONS']['NgnPsAdminState']=="disabled":
	        logger.info("Disabling NGNPS")
                testcase.disable_ngnps()
    testcase.restart_mps()
    supported_CONN_tests=['IcRateAvg', 'IcRatePeak']
    supported_MP_tests=['MpIcP0Y', 'MpIcP0G']
    for i in config['DRMP1']:
        if i=='MPTEST':
            for j in config['DRMP1'][i]:
                if j in supported_MP_tests:
                    matchObj=re.search('[0-9]{1,2}',j)
                    set_priority(client_scenario,int(matchObj.group()))
                    ClientPeerNode=PeerNode(**config['CLIENTPEERNODE'])
                    ServerPeerNode=PeerNode(**config['SERVERPEERNODE'])
                    testcase.add_peernode(ClientPeerNode)
                    testcase.add_peernode(ServerPeerNode)

                    if j.endswith('Y'):
                        capcCfgSet1=CapacityConfigSet(**config['CAPACITYCONFIGSETYELLOW'])
                        testcase.add_capacity_config_set(capcCfgSet1)
                        clientConnection=Connection(**config['CLIENTCONNECTION'])
                        clientConnection.capacityCfgSetName=capcCfgSet1.name
                        clientConnection.peerNodeName=ClientPeerNode.name
                        testcase.add_connection(clientConnection)


                    if j.endswith('G'):
                        capcCfgSet2=CapacityConfigSet(**config['CAPACITYCONFIGSETGREEN'])
                        testcase.add_capacity_config_set(capcCfgSet2)
                        clientConnection=Connection(**config['CLIENTCONNECTION'])
                        clientConnection.capacityCfgSetName=capcCfgSet2.name
                        clientConnection.peerNodeName=ClientPeerNode.name
                        testcase.add_connection(clientConnection)
                    serverConnection=Connection(**config['SERVERCONNECTION'])
                    serverConnection.peerNodeName=ServerPeerNode.name
                    testcase.add_connection(serverConnection)
		    testcase.enable_connection(client_connection)
		    testcase.enable_connection(server_connection)
                    test_status=run_test(client_scenario,server_scenario,testcase)
                    if test_status==1:
			peg_expected=CALL_RATE*300
                        peg_value=collect_counters(testcase,j)
			logger.info("Peg value=%s",peg_value)
			t_end=time.time()+300
			while True:
			    while time.time() < t_end:
			        sleep(10)
			        """
			        if peg_value==0:
				    peg_value=collect_counters(testcase,j)
				    continue
				if peg_value>0 and peg_value<2997:
				    peg_value=collect_counters(testcase,j)
				    #logger.info("Peg value=%s",peg_value)
				    sleep(10)
				    continue
				if peg_value>2997 and peg_value<3005:
				    logger.info("Peg value=%s",peg_value)
				    logger.info("Test pass")
				    break
				else:
				    logger.error("Invalid Peg counter")
			            break
				"""
	                    peg_value=collect_counters(testcase,j)
	                    if peg_value>2500 and peg_value<3005:
			        logger.info("Peg value=%s",peg_value)
			        logger.info("Test pass")
			        break
	                    else:
			        logger.error("Invalid Peg counter")
			        break
                    logger.info("cleaning up seagull processes")
		    ShellCommand("killall seagull")
		    #testcase.disable_connection(client_connection)
		    #testcase.disable_connection(server_connection)
		    sleep(5)
		    #testcase.delete_connection(clientConnection)
		    #testcase.delete_connection(serverConnection)
		    #testcase.delete_peernode(ClientPeerNode)
		    #testcase.delete_peernode(ServerPeerNode)
		    #testcase.delete_capacity_config_set(clientConnection.capacityCfgSetName)
		    clean_dsr_config={}
		    clean_dsr_config['test']=testcase
		    clean_dsr_config['connection']=[clientConnection,serverConnection]
		    clean_dsr_config['peernode']=[ClientPeerNode,ServerPeerNode]
		    clean_dsr_config['capacity_config_set']=[clientConnection.capacityCfgSetName]
		    clean_dsr(**clean_dsr_config)

    """
    for i in config['DRMP1']['MPTEST']:
        if i in supported_CONN_tests:
            print("Verify ",i)
    """
if __name__ == '__main__':
   main(sys.argv[1])	
