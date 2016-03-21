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





web = \
{   "channel_id":"C0G4HUYJ1",
    "team_domain":"mycomp",
    "channel_name":" NEWchannel",
    "user_name":"Fred",
    "user_id" :"U0G0Y8D7A",
    "command":"/starleaf",
        "response_url":"http://127.0.0.0:8000/",
    "text":""
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
    }
}


email0 = { \
"headers":'this is headers',
"to":'new@cloud.sl, William MacDonald <william.macdonald@gmail.com>, William MacDonald <william.macdonald@starleaf.com>',
"cc":"fred@fred",
"from":"fred0_123@fred.co.ik.will",
"subject":'thi is subuj',
"envelope":json.dumps({"to":'fred@fred.com',"from":'john@webex.com'}),
"attachments":'1',
"attachment-info":json.dumps(files)
}

email = { \
"headers":'this is headers',
"to":'new@cloud.sl, William MacDonald <william.macdonald@gmail.com>, William MacDonald <william.macdonald@starleaf.com>',
"cc":"fred@fred",
"from":"fred0_123@fred.co.ik.will",
"subject":'thi is subuj',
"text":'Skype Meeting<https://meet.lync.com/starleaf1/william.macdonald/03ZIU1XF>',
"envelope":json.dumps({"to":'fred@fred.com',"from":'john@webex.com'}),
"attachments":'0'}

form = { "password":"wombat","user_id":"U0G0Y8D7A", "email":"will@fred.com"}

headers = {'Content-type': 'application/json'}
headers = {'Content-type': 'multipart/form-data'}

session = requests.Session()
print "calling..."
#url='http://127.0.0.1:8000/slack/'
#r = session.get(url,params=web)
#c=r.status_code
#t=r.text
#print 'Response code is:', c
#if c == 500:
#    i = t.find('<div id="summary">')
#    print t[i:i+300]
#    exit()
#else:
#    print 'Body text is:\n', t
#exit()

f = open("/users/will/new.ics",'rb')
files = {'attachment1':f}
url='http://127.0.0.1:8000/email/'
r = session.post(url,data=email,files=files, verify=False)
#r = session.post(url,data=form)
c=r.status_code
t=r.text
print 'Response code is:', c
if c == 500:
    i = t.find('<div id="summary">')
    print t[i:i+300]
    exit()
else:
    print 'Body text is:\n', t
