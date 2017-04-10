#!/usr/bin/python
from pyMMI import MMI
from pprint import pprint
import json
import sys
import urllib

def mmi_get_counter(**kwargs):
    query_string={}
    if kwargs is not None:
	for key, value in kwargs.iteritems():
	    if key != 'client':
		query_string[key] = value
	#print query_string
	string = urllib.urlencode(query_string)
	query_result = 'mon/measurements/data?' + string
    for key, value in kwargs.iteritems():
	if key == 'client':
	    response = value.GetDsr(query_result)
	    break
    #out_json = (response.json().get("data"))
    #get_response_json = json.dumps(out_json)
    return response

if __name__ == "__main__":
    client = MMI(sys.argv[1])
    args={}
    args['scope_type']="ServerGroup"
    args['time_count']="-5"
    args['client']=client
    mmi_get_counter(**args)
