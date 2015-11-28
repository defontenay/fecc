import requests
import socket
import time
import json



email = \
    {'text': 'body of email',
    'attachments': 3,
    'subject': "hello world",
    'permanent': False,
}

headers = {'Content-type': 'application/json'}
session = requests.Session()
url='http://127.0.0.1:8000/email'
#url='http://fecc.starleaf.com/email'

r = session.post(url,data=json.dumps(email),headers=headers, verify=False)
print 'Response code is:', r.status_code
print 'Body text is:', r.text


