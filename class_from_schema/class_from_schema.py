#!/usr/bin/python

import json
import python_jsonschema_objects as pjs
import os
import re
import pprint


BaseClasses={}
for filename in os.listdir("/home/raleigh/joalphon/DRMP_Scripts/scripts/"):
	if filename.endswith(".json"):
		builder=pjs.ObjectBuilder(filename)
		ns=builder.build_classes()
		BaseClasses[re.sub(".json","",filename)]=ns.ExampleSchema


class LocalNode(BaseClasses["localnode"]):
	def __init__(self,*args,**kwargs):
		super(LocalNode,self).__init__(**kwargs)


class PeerNode(BaseClasses["peernode"]):
	def __init__(self,*args,**kwargs):
		super(PeerNode,self).__init__(**kwargs)

class Connection(BaseClasses["connection"]):
	def __init__(self,*args,**kwargs):
		super(Connection,self).__init__(**kwargs)

class CapacityConfigSet(BaseClasses["capacity_configuration_set"]):
        def __init__(self,*args,**kwargs):
                super(CapacityConfigSet,self).__init__(**kwargs)



if __name__ == '__main__':
	ip=[]
	dic={}
	ip.append(dic)
	ip[0]['ipAddr']="10.10.10.10"
	ip[0]['ipType']="LocalIp"
	LN1=LocalNode(name="JoseLN1",realm="oracle.com",fqdn="dsr.oracle.com",cexCfgSetName="Default",radiusClientPortEnabled=False,connCfgSetName="Deafault",certVerifyMode="SslVerifyNone",ip=ip)

	print LN1.serialize()
