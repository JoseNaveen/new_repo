#!/usr/bin/python

import paramiko

def enable_drmp(DSR_SO):
    client=paramiko.Transport((DSR_SO,22))
    client.connect(username='admusr',password='Dukw1@m?')
    session=client.open_channel(kind='session')
    session.exec_command("/opt/appworks/bin/gcli update Options '16PrioritiesMode'='enabled'")

def disable_drmp(DSR_SO):
    client=paramiko.Transport((DSR_SO,22))
    client.connect(username='admusr',password='Dukw1@m?')
    session=client.open_channel(kind='session')
    session.exec_command("/opt/appworks/bin/gcli update Options '16PrioritiesMode'='disabled'")
