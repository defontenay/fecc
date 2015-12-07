

import requests
import json
import re
import hashlib
import hmac
import re
import pbkdf2
import binascii
import pytz
import time
import warnings
from starleaf import StarLeafClient
from datetime import datetime, timedelta



headers = {'Content-type': 'application/json'}
LOGFILE = "./satic.log"
warnings.filterwarnings("ignore")
apiServer='https://portal.starleaf.com/v1'

starleafConference = {'title': 'conf',
    'description': 'This conference was created from Slack.',
    'timezone': 'UTC',
    'permanent': False,
    'start': " ",
    'end': " ",
    'participants': [ ],
}

join =      "You have been invited to jump on a StaLeaf video call\n"
join +=     "From Breeze click https://portal.starleaf.com/breezelinks/redirect?dial=<uri>\n"
join +=     "or press the green button, or dial <conf-id>\n"
join +=     "from your telephone, dial USA:+1 888 998 5260 or UK:+44 330 828 0796 and enter access code <conf-id>"

def log(logdata,header=""):
    print  header, logdata


def json_log(logdata,header=""):
    try:
        string = json.dumps(logdata, sort_keys=True, indent=4, separators=(',', ': '))
    except:
        string = "No JSON"
    print header
    print string

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
            log ("Need to authenticate")
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
        log ( str(response.status_code),'Response code is:' )
        try:
            body = response.json()
        except ValueError:
            return None
        else:
            json_log (body,"RESPONSE")
            if not body['ok']:
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


def look_up_user(slack_id):
    return ("wmm+185@starleaf.com","wombat")


def StarLeafSlack(data):
    slack = SlackClient("xoxp-4281906585-4695033383-16028628019-ca364cc223", "https://slack.com/api/")
    if not slack.authenticate():
        return "Cloud error"
    channel_id=data.get("channel_id")
    user_id=data.get('user_id')
    command=data.get("command")
    text=data.get("text")
    name = data.get("user_name")
    dom=data.get("team_domain")
    chan=data.get("channel_name")
    body = slack.getUser(user_id)
    result = "Did not work"
    if body:
        # email, password = look_up_user(user_id)
        email = None                        # this will force it to use the slack email
        password = "wombat"
        if not email:
            email = body['user']['profile']['email']
            m1 = re.search('pw=(\S+)\s', text)
            m2 = re.search('em=([a-zA-Z0-9-.+_]{4,64}@[a-zA-Z0-9-.]{0,62}?)\s', text)
            if m1:
                password = m1.group(1)
            if m2:
                email = m2.group(1)
        if not password:
            string =    "First time using StarLeaf ?\n"
            string +=   "Use /starleaf pw=<pass> where <pass> is your StarLeaf Breeze password\n"
            string +=   "If "+email+" is not your StarLeaf email then do\n"
            string +=   "/starleaf pw=<pass> em=<email> where <email> is your StarLeaf email"
            return string

        star = StarLeafClient(username=email,password=password,apiServer=apiServer)
        if not star.authenticate():
            return("we failed to log you onto the StarLeaf cloud, please check your settings")

        starleafConference['title'] = name+" "+chan+" "+dom                  # start building the conference
        starleafConference['start'] = datetime.utcnow().isoformat()
        starleafConference['end'] =  (datetime.utcnow() + timedelta(minutes=5)).isoformat()

        ch_body = slack.getChannel(channel_id)          # grabe the channel details
        members = ch_body['channel']['members']     #then go through the memenbers
        for uid in members:
            em2, pw2 = look_up_user(uid)
            if em2:
                dest = {"email": em2}    # if they have a different SL address then add that too
            else:
                usr_body = slack.getUser(uid)                                # get the users details
                dest = {"email":usr_body['user']['profile']['email']}       #mainly emai address
            starleafConference['participants'].append(dest)                # add to list odf invitees
        conf = star.createConf(starleafConference)
        try:
            dial = conf['dial_info']
        except:
            return "Failed to create the conference"

        string = join.replace("<uri>",dial['dial_standards'])
        result= string.replace("<conf-id>",dial['access_code_pstn'])
    return result



"""
    
web = \
{   "channel_id":"C0489SNJ9",
    "team_domain":"mycomp",
    "channel_name":"thischannel",
    "user_name":"Fred",
    "user_id" :"U0G0Y8D7A",
    "command":"/starleaf",
    "text":"pw=freddy"
}



print StarLeafSlack(web)
exit()

slack = SlackClient("xoxp-4281906585-4695033383-16028628019-ca364cc223", "https://slack.com/api/")
if not slack.authenticate():
    exit()
b = slack.getChannels()
for i in range(10):
    ch = b['channels'][i]['id']
    b = slack.getChannel(ch)
    m = b['channel']['members']
    for u in m:
        b = slack.getUser(u)
        if b:
            e = b['user']['profile']['email']
            n = b['user']['name']
            print u," ",n," has email: ",e
"""

                         

                         
                         






