#!/usr/bin/python

from pyMMI import *

def getActiveSOAM(DSRNO):
    resp=DSRNO.GetDsr('topo/servergroups')
    SOAMSGS=[i['name'] for i in resp.json()['data'] if i['level']=="B"]
    servers=DSRNO.GetDsr('topo/servers')
    SOAMSG_SERVERS={}
    for i in SOAMSGS:
        SOAMSG_SERVERS[i]=[]
        for j in servers.json()['data']:
            if j['serverGroupName']==i:
                SOAMSG_SERVERS[i].append(j['hostname'])
    SG_ACTIVE={}
    for k in SOAMSG_SERVERS:
        for j in SOAMSG_SERVERS[k]:
            status=DSRNO.GetDsr('topo/servers/' + j + '/status')
            if status.json()['data']['haRole']=="Active":
                SG_ACTIVE[k]=j
    for SG in SG_ACTIVE:
        SO_OBJ=MMI(SG_ACTIVE[SG])
        return SO_OBJ,SG_ACTIVE[SG] #returns Active SOAM MMI object and hostname
