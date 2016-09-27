import requests
import socket
import time
import json
import warnings

web=    \
    {"message_id": "2889",
    "message_type": "comment_posted",
    "binder_id": "BAGUChIRH7P7eBdR9h9nyR5",
    "callback_url": "https://api.moxtra.com/webhooks/CAEqBS8wcXkzehdCQUdVQ2hJUkg3UDdlQmRSOWg5bnlSNYABvBaQAxQ",
    "event": {
        "timestamp": "2016-04-25T23:17:10Z",
            },
    "user": {
        "id": "Utkj3YC5BxRHCCaq9widP67",
        "name": "Joe Smith"
    },
    "comment": {
        "id": "2888",
        "text": "what is a bot?",
        "audio": "null",
    },
    "target": {
        "id": "BAGUChIRH7P7eBdR9h9nyR5",
        "object_type": "binder",
} }


headers = {'Content-type': 'application/json'}
warnings.filterwarnings("ignore")
url='http://127.0.0.1:8000/moxtra'
#url='http://127.0.0.1:8000/zapcal/test@test.com'
##url='http://fecc.starleaf.com/zapcal/will@starleaf.com'
web3 = { \
    "end__dateTime":'2016-09-17T15:30:00Z', \
    "Subject":'Wills New Meeting',\
    "start__dateTime":'2016-09-17T02:00:00-07:00',\
    "iCalUId":'willsuniqusssssd2',\
    "IsCancelled":'True',\
    "StartTimeZone":'Pacific',\
    "description":' <font size="4"><span style="font-size:16pt"><a href="https://meet.lync.com/starleaf1/william.macdonald/3XZN1VDW" target="_blank">Join online meeting </a>'   }

session = requests.Session()

print "calling...",url
args = json.dumps(web, sort_keys=True, indent=4, separators=(',', ': '))

r = session.post(url,data=args, headers=headers, verify=False)
c=r.status_code
t=r.text
print 'Response code is:', c
if c == 500:
    i = t.find('<div id="summary">')
    print t[i:i+300]
    exit()
else:
    print 'Body text is:\n', t
