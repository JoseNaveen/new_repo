#!/usr/bin/python

import paramiko

def enable_ngnps(DSR_SO):
    client=paramiko.Transport((DSR_SO,22))
    client.connect(username='admusr',password='Dukw1@m?')
    session=client.open_channel(kind='session')
    session.exec_command("/opt/appworks/bin/gcli update Options 'NgnPsAdminState'='enabled'")

def disable_ngnps(DSR_SO):
    client=paramiko.Transport((DSR_SO,22))
    client.connect(username='admusr',password='Dukw1@m?')
    session=client.open_channel(kind='session')
    session.exec_command("/opt/appworks/bin/gcli update Options 'NgnPsAdminState'='disabled'")
