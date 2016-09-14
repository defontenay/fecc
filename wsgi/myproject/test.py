import requests
import socket
import time
import json
import warnings




headers = {'Content-type': 'application/json'}
warnings.filterwarnings("ignore")
url='http://127.0.0.1:8000/zapcal/email'
url='http://fecc.starleaf.com/zapcal/email'
web = {   "value1":"hello world", "V2":"Goodbye world"}
session = requests.Session()

print "calling...",url

r = session.post(url,data=web, verify=False)
c=r.status_code
t=r.text
print 'Response code is:', c
if c == 500:
    i = t.find('<div id="summary">')
    print t[i:i+300]
    exit()
else:
    print 'Body text is:\n', t
