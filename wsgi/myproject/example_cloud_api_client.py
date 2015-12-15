import requests
import socket
import time
import json
import warnings




headers = {'Content-type': 'application/json'}
warnings.filterwarnings("ignore")
apiServer='https://portal.starleaf.com/v1'
token = "xoxp-4281906585-16032285248-16324528194-a1f404b085"


class SlackClient(object):
    """
        This is a client implementing the SS=lack API  1.
        """
    
    # The address of the API server should be passed into the constructor,
    # if different from the default.
    
    
    
    def __init__(self, token,  apiServer, sslVerify=False):
        self.apiServer = apiServer
        self.token = token
        self.sslVerify = sslVerify
        self.session = requests.Session()
    
    def _get(self, path, params=None):
        r = self.session.get(self.apiServer + path, params=params, verify=self.sslVerify)
        return self._getBody(r)
    
    def _post(self, path, body):
        r = self.session.post(self.apiServer + path, data=json.dumps(body), headers=headers, verify=self.sslVerify)
        return self._getBody(r)
    
    def _put(self, path, body):
        r = self.session.put(self.apiServer + path, data=json.dumps(body), headers=headers, verify=self.sslVerify)
        if r.status_code == 401:
            #   print ("Need to authenticate")
            self.authenticate()
            r = self.session.put(self.apiServer + path, data=json.dumps(body), headers=headers, verify=self.sslVerify)
        return self._getBody(r)
    
    def _delete(self, path):
        r = self.session.delete(self.apiServer + path, verify=self.sslVerify)
        if r.status_code == 401:
            self.authenticate()
            r = self.session.delete(self.apiServer + path, verify=self.sslVerify)
        return self._getBody(r)
    
    @staticmethod
    def _getBody(response):
        print str(response.status_code),'Response code is:'
        try:
            body = response.json()
        except ValueError:
            return None
        else:
            if not body['ok']:
                #print json.dumps(body, sort_keys=True, indent=4, separators=(',', ': '))
                return None
            return body

    def authenticate(self):
        params = {'token': self.token}
        body = self._get('/auth.test', params=params)
        return body

    def getChannel(self, channelId):
        params = {'token': self.token, 'channel': channelId}
        body = self._get('/channels.info', params=params)
        return body

    def getUser(self, userId):
        params = {'token': self.token, 'user': userId}
        body = self._get('/users.info', params=params)
        return body
    
    def getChannels(self):
        params = {'token': self.token}
        body = self._get('/channels.list', params=params)
        return body





web0 = \
{   "channel_id":"C0G4HUYJ1",
    "team_domain":"mycomp",
    "channel_name":" NEWchannel",
    "user_name":"Fred",
    "user_id" :"U0G0Y8D7A",
    "command":"/starleaf",
        "response_url":"http://127.0.0.0:8000/",
    "text":"m=1  u=will@starleaf.com,fred@me.org"
}

"""
slack = SlackClient(token, "https://slack.com/api/")
slack.authenticate()
slack.getChannels()
exit()
"""

files = { \
    "attachment1": {
        "filename": "new.ics",
        "name": "new.ics",
        "type": "text/calendar"
    },
    "attachment2": {
        "charset": "us-ascii",
        "type": "text/html"
    }
}

email = { \
"headers":'this is headers',
"to":'fred@fred.com',
"subject":'thi is subuj',
"envelope":json.dumps({"to":'fred@fred.com',"from":'john@webex.com'}),
"attachments":2,
"attachment-info":json.dumps(files)
}

                             
                             
headers = {'Content-type': 'application/json'}
headers = {'Content-type': 'multipart/form-data'}

session = requests.Session()
url='http://127.0.0.1:8000/email/'
f = open("/users/will/new.ics",'rb')
files = {'attachment2':f , 'attachment1':f}
print f.read()
r = session.post(url,data=email,files=files, verify=False)
#r = session.get(url,params=web0, headers=headers)
c=r.status_code
t=r.text
print 'Response code is:', c
if c == 500:
    i = t.find('<div id="summary">')
    print t[i:i+300]
    exit()
else:
    print 'Body text is:\n', t
