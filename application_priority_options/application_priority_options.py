#!/usr/bin/python
import paramiko
import logging
from logging.config import fileConfig
fileConfig('logging_config.ini')
logger = logging.getLogger()
def app_prty_opt_insert():
    pass


def app_prty_opt_update(**a):
    client=paramiko.Transport((a['DSRSO'],22))
    client.connect(username='admusr',password='Dukw1@m?')
    session=client.open_channel(kind='session')
    logger.info("/opt/appworks/bin/gcli update ApplicationPriorityOptions 'AppName'=" + "'" + a['AppName'] + "','appId'=" + "'" + a['appId'] + "','DrmpAnswerAdmin'=" + "'" + a['DrmpAnswerAdmin'] + "','Ngn3gppAdmin'=" + "'" + a['Ngn3gppAdmin'] + "','NgnDrmpAdmin'=" + "'" + a['NgnDrmpAdmin'] + "','DrmpRequestAdmin'=" + "'" + a['DrmpRequestAdmin'] + "'")
    session.exec_command("/opt/appworks/bin/gcli update ApplicationPriorityOptions 'AppName'=" + "'" + a['AppName'] + "','appId'=" + "'" + a['appId'] + "','DrmpAnswerAdmin'=" + "'" + a['DrmpAnswerAdmin'] + "','Ngn3gppAdmin'=" + "'" + a['Ngn3gppAdmin'] + "','NgnDrmpAdmin'=" + "'" + a['NgnDrmpAdmin'] + "','DrmpRequestAdmin'=" + "'" + a['DrmpRequestAdmin'] + "'")
