

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
import threading
from starleaf import StarLeafClient
from datetime import datetime, timedelta

list = []
class User(object):

    def __init__(self):
        self.slack = ""
        self.email = ""
        self.password = ""
        self.error = ""
    
    def __str__(self):
        return self.slack+"  "+self.email+"   "+self.password

    def save(self):
        list.append(self)

    def get(self, id):
        for u in list:
            if u.slack == id:
                return(u)



#    from users.models import User



headers = {'Content-type': 'application/json'}
LOGFILE = "./satic.log"
warnings.filterwarnings("ignore")
apiServer='https://portal.starleaf.com/v1'


join =      "<@<uid>> has invited you to a StaLeaf video call\n"
join +=     "From Breeze click  <https://portal.starleaf.com/breezelinks/redirect?dial=<uri>|here\n"
join +=     "or press the green button, or dial <conf-id>\n"
join +=     "from your telephone, dial USA:+1 888 998 5260 or UK:+44 330 828 0796 and enter access code *<conf-id>*"

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
        #   log ( str(response.status_code),'Response code is:' )
        try:
            body = response.json()
        except ValueError:
            return None
        else:
            #            json_log (body,"RESPONSE")
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


def look_up_user(id):
    u = User()
    return u.get(id)
    try:
        user = User.objects.get(slack = id)
    except:
        return None
    return user

def make_user(id, email, password):
    user = User()
    user.slack = id
    user.email = email
    user.password = password
    user.error = ""
    user.save()
    return user

def StarLeafSlack(data):
    slack = SlackClient("xoxp-4281906585-4695033383-16028628019-ca364cc223", "https://slack.com/api/")
    if not slack.authenticate():
        return "Cloud error"
    user_id=data.get('user_id')
    text=data.get('text')
    body = slack.getUser(user_id)
    if body:
        user = look_up_user(user_id)
        if not user:
            email = body['user']['profile']['email']
            print text, " no previous user ", email
            m1 = re.search('pw=(\S+)\s*', text)
            m2 = re.search('em=([a-zA-Z0-9-.+_]{4,64}@[a-zA-Z0-9-.]{0,62}?)\s', text)
            password = None
            if m1:
                print "found a password"
                password = m1.group(1)
            if m2:
                print "found an email"
                email = m2.group(1)
            if password:
                user = make_user(user_id,email,password)
                result = "Your pasword has been saved\nscheduling your conference now"
        if not user:
            string =    "First time using StarLeaf?\n"
            string +=   "Use */starleaf pw=password* where password is your StarLeaf Breeze password\n"
            string +=   "If "+email+" is not your StarLeaf email then...\n"
            string +=   "Use */starleaf pw=<password em=me@dom.com* where me@dom.com is your StarLeaf email"
            return string
        if user.error != "":
            string = "Your previous error was\n"
            string += user.error
            user.error = ""
            user.save()
            return string
    
        result = "scheduling your conference now"
    else:
        result = "Weird error"

    thread1 = threading.Thread(target=makeConference, args = (slack,user,data))
    thread1.start()

    return result


def makeConference(slack,user,data):
                               
    starleafConference = {'title': 'conf',
    'description': 'This conference was created from Slack.',
    'timezone': 'UTC',
    'permanent': False,
    'start': " ",
    'end': " ",
    'participants': [ ],   }
    
    print "NEW Spawned Process:"

    channel_id=data.get("channel_id")
    name = data.get("user_name")
    dom=data.get("team_domain")
    chan=data.get("channel_name")
                               
    star = StarLeafClient(username=user.email,password=user.password,apiServer=apiServer)
    if not star.authenticate():
        user.error = " Failed to autheticate"
        print "KILL faled to authentivate"
        user.save()
        return
    
    print "Authenticated"

    starleafConference['title'] = name+" "+chan+" "+dom                  # start building the conference
    starleafConference['start'] = datetime.utcnow().isoformat()
    starleafConference['end'] =  (datetime.utcnow() + timedelta(minutes=5)).isoformat()

    ch_body = slack.getChannel(channel_id)          # grabe the channel details
    members = ch_body['channel']['members']     #then go through the memenbers
    for uid in members:
        guest = look_up_user(uid)
        if guest:
            guest = {"email": guest.email}    # if they have a different SL address then add that too
        else:
            gst_body = slack.getUser(uid)                                # get the users details
            dest = {"email":gst_body['user']['profile']['email']}       #mainly emai address
        starleafConference['participants'].append(dest)                # add to list odf invitees
    conf = star.createConf(starleafConference)
    try:
        dial = conf['dial_info']
    except:
       user.error = "KILL Failed to create conf"
       user.save()
       return
    
    url = data.get("response_url")
    uri = join.replace("<uri>",dial['dial_standards'])
    conf = uri.replace("<conf-id>",dial['access_code_pstn'])
    post = conf.replace("<uid>",uid)
                               
    session = requests.Session()
    parms = {"text":post}
    print json_log(parms)
    print "URL is ", url
    r = session.post(url,headers=deaders,data=parms)
    if r.status_code != 200:
        user.error = "POST error "+str(r.status_code)
        usr.save()
    print r.body
    print "KILL normal"
    return





web0 = \
{   "channel_id":"C0489SNJ9",
    "team_domain":"mycomp",
    "channel_name":"thischannel",
    "user_name":"Fred",
    "user_id" :"U0G0Y8D7A",
    "command":"/starleaf",
    "text":""
}


web1 = \
{   "channel_id":"C0489SNJ9",
    "team_domain":"mycomp",
    "channel_name":"thischannel",
    "user_name":"Fred",
    "user_id" :"U0G0Y8D7A",
    "command":"/starleaf",
    "text":"pw=fred"
}


web2 = \
{   "channel_id":"C0489SNJ9",
    "team_domain":"mycomp",
    "channel_name":"thischannel",
    "user_name":"Fred",
    "user_id" :"U0G0Y8D7A",
    "command":"/starleaf",
    "text":""
}




#print StarLeafSlack(web0)


                         
                         






