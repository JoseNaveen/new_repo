#!/usr/bin/python

import yaml
from class_from_schema import *
import sys
from pyMMI import *
if __name__ == '__main__':
    """
    ip=[]
    dic={}
    ip.append(dic)
    ip[0]['ipAddr']="10.10.10.10"
    ip[0]['ipType']="LocalIp"
    LN1=LocalNode(name="JoseLN1",realm="oracle.com",fqdn="dsr.oracle.com",cexCfgSetName="Default",radiusClientPortEnabled=False,connCfgSetName="Deafault",certVerifyMode="SslVerifyNone",ip=ip)

    print LN1.serialize()
    """
    yaml_config=open('config.yaml')
    config=yaml.load(yaml_config)
    yaml_config.close()
    print config['CAPACITYCONFIGSETYELLOW']
    CapcCfgSet1=CapacityConfigSet(**config['CAPACITYCONFIGSETYELLOW'])
    CapcCfgSet2=CapacityConfigSet(**config['CAPACITYCONFIGSETGREEN'])
    print CapcCfgSet1.serialize()
    dsr=MMI(sys.argv[1])
    resp=dsr.PostDsr('diameter/capacityconfigurationsets',CapcCfgSet1.serialize())
    print resp.text
    resp=dsr.PostDsr('diameter/capacityconfigurationsets',CapcCfgSet2.serialize())
    print resp.text
    """
    resp=dsr.DeleteDsr('diameter/capacityconfigurationsets','CapcCfgSetYellow')
    print resp.text
    resp=dsr.DeleteDsr('diameter/capacityconfigurationsets','CapcCfgSetGreen')
    print resp.text
    """
    ClientPeerNode=PeerNode(**config['CLIENTPEERNODE'])
    resp=dsr.PostDsr('diameter/peernodes',ClientPeerNode.serialize())
    print resp.text
