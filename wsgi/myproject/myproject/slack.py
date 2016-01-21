

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
from datetime import datetime, timedelta
from settings import LOGFILE, STATIC_ROOT
from starleaf import StarLeafClient
from users.models import User
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt



headers = {'Content-type': 'application/json'}
warnings.filterwarnings("ignore")
apiServer='https://portal.starleaf.com/v1'
token = "xoxp-4281906585-16032285248-16324528194-a1f404b085"

help_text =  "This creates a new StarLeaf conference, with you as moderator\n"
help_text+=  "Users will get a Breeze link to click and the dial-in number\n"
help_text+=  "for PSTN. All members of this channel will get a Green Button\n"
help_text+=  "if they are a StarLeaf user. Its named after this Slack Channel\n"
help_text+=  "You need to tell me your StarLeaf password by typing\n"
help_text+=  "     */starleaf   pw=password*   \n"
#help_text+=  "and if you use a different email on StaLeaf tell me that too\n"
#help_text+=  "     */starleaf   em=my@email.com    pw=password*   \n"
help_text+=  "If you set the wrog email or password you can reset it with.. \n"
help_text+=  "     */starleaf   delete*   \n"
help_text+=  "to make a longer conference add the length, in mins or hours e.g.\n"
help_text+=  "     */starleaf   h=1 m=30*  (default is m=5) \n"
help_text+=  "you can invite other people (not in this channel) too \n"
help_text+=  "     */starleaf   u=will@starleaf.com,fred@gmail.com  *   \n"



join =      "<@<uid>> has invited you to a StaLeaf video call\n"
join +=     "- Breeze users can click  <https://portal.starleaf.com/breezelinks/redirect?dial=<uri>|here>\n"
join +=     "- Or press the green button, or dial <conf-id> on StarLeaf\n"
join +=     "- from a phone, dial the local number and use the code *<conf-id>*\n"
join +=     "- Local numbers are.. USA:+1 888 998 5260 or UK:+44 330 828 0796\n"
join +=     " -With Lync, H.323 or SIP dial <uri> or click <<url>|here>\n "

pw_page =' <html> <head> <title>StarLeaf Credentials</title> </head> \
<body> \
<form name="Account Details" action="/slackpw" method="POST"> \
Slack IDl :\
<br> <input type="text" name="user_id" value="<id>" size="20">      \
<br><br> \
StarLeaf Email :\
<br> <input type="text" name="email" value="<email>" size="50">      \
<br><br> \
Enter StarLeaf Password : <br> <input type="password" name="password" size="25">    \
<br><br>   \
<input type="submit" value="submit"">  \
</div> </form> </body> </html>'



###############################################################################

def page(data):
    print data.META['HTTP_HOST']
    if data.method != 'GET':
        return HttpResponse('INVALID_METHOD')

    try:
        id = data.GET.get('user_id',"slackid")
        email = data.GET.get('email',"email")
        np1 = pw_page.replace("<email>",email)
        np2 = np1.replace("<id>",id)
        return HttpResponse(np2)
    except:
        return HttpResponse('Exception')

###############################################################################

def log(logdata,header=""):
    log = open(LOGFILE, 'a')
    log.write(str(datetime.now())+"--------------------\n")
    if len(header) > 0:
        log.write(header+"\n")
    if "static" in LOGFILE:
        print  header, logdata
    if logdata:
        log.write(logdata)
    else:
        log.write("None")
    log.write("\n")
    log.close()
    return 0



def json_log(logdata,header=""):
    log = open(LOGFILE, 'a')
    log.write(str(datetime.now())+"--------------------\n")
    if len(header) > 0:
        log.write(header+"\n")
    try:
        string = json.dumps(logdata, sort_keys=True, indent=4, separators=(',', ': '))
    except:
        string = "No JSON"
    log.write(string)
    if "static" in LOGFILE:
        print header
        print string
    log.write("\n")
    log.close()
    return 0



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
        #log ( str(response.status_code),'Response code is:' )
        try:
            body = response.json()
        except ValueError:
            return None
        else:
            if not body['ok']:
                json_log (body,"ERROR RESPONSE")
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
    try:
        user = User.objects.get(slack = id)
    except:
        return None
    return user

def make_user(id):
    user = User(slack = id, email = "", password = "",error = "")
    user.save()
    return user

def StarLeafSlack(data):
    slack = SlackClient(token, "https://slack.com/api/")
    if not slack.authenticate():
        log ("Slack error, failed to authenticate - maybe token?")
        return "Cloud TOKEN error"
    user_id=data.get('user_id')
    text=data.get('text')

    if not user_id:
        return "No user id argument"

    if not text:
        text = ""

    if "delete-all" in text:
        l  = User.objects.all()
        for u in l:
            u.delete()
        return "Deleted ALL records"

    if "help" in text:
        return help_text

    body = slack.getUser(user_id)
    result = ""
    if body:
        user = look_up_user(user_id)
        if user and "delete" in text:
            user.delete()
            return "Deleted"
        if not user or len(user.password) is 0:
            email = body['user']['profile']['email']
            if user:
                log(email," has not set PW ")
            else:
                user = make_user(user_id)
                user.email = email
                log ( email, " no previous entry set for ")
            m1 = re.search(r'pw=(\S+)', text)
            m2 = re.search(r'em=([a-zA-Z0-9-.+_]{1,64}@[a-zA-Z0-9-.]{3,62})', text)
            if m1:
                user.password = m1.group(1)
                log( "found a password ",user.password )
                result += "Your pasword has been saved\n"
            if m2:
                user.email= m2.group(1)
                log ( "found an email ",user.email )
                result += "Your alternative email has been saved\n"
            user.save()
                                 
        if len(user.password) == 0:
    #        string =   "Use */starleaf pw=pass* where pass is your Breeze password"
            string =  " click  <http://"+data.META['HTTP_HOST']+"/slackpw?user_id="+user_id+"&email="+email+">|here> to set password.....\n"
            return string
                                 
        if user.error != "":
            result += "Your previous error was\n"
            result += user.error
            user.error = ""
            user.save()

        result += "scheduling your conference now"
        thread1 = threading.Thread(target=makeConference, args = (slack,user,data))
        thread1.start()
    else:
        result += "Weird error"

    return result


def makeConference(slack,user,data):
                               
    starleafConference = {'title': 'conf',
    'description': 'This conference was created from Slack.',
    'timezone': 'UTC',
    'permanent': False,
    'start': " ",
    'end': " ",
    'participants': [ ],   }
    
    channel_id=data.get("channel_id")
    name = data.get("user_name")
    dom=data.get("team_domain")
    chan=data.get("channel_name")
    text=data.get('text')
    log("user "+ user.slack+ " em  "+user.email+"  pw  "+user.password+" ch "+channel_id+" dom "+dom+" chn "+chan,"NEW SPAWN " )
    
    star = StarLeafClient(username=user.email,password=user.password,apiServer=apiServer)
    if not star.authenticate():
        user.error = " Failed to autheticate"
        log( "KILL -SL faled to authentivate")
        user.save()
        return
    
    log ("SL Authenticated")

    m1 = re.search('m=([0-9]{1,2})', text)
    h1 = re.search('h=([0-9]{1,2})', text)

    mins = 0
    if m1:
        mins += int(m1.group(1))
    if h1:
        mins += 60*(int(m1.group(1)))
    if mins == 0:
        mins = 5

    ems = re.findall(r'(?:u=|(?<=,))([a-zA-Z0-9-.+_]{1,64}@[a-zA-Z0-9-.]{3,62})(?:,|\s|$)+', text)
    for em in ems:
        dest = {"email":em}
        starleafConference['participants'].append(dest)

    starleafConference['title'] = chan                 # start building the conference
    starleafConference['start'] = datetime.utcnow().isoformat()
    starleafConference['end'] =  (datetime.utcnow() + timedelta(minutes=mins)).isoformat()

    ch_body = slack.getChannel(channel_id)          # grabe the channel details
    if not ch_body:
        members =[]
    else:
        members = ch_body['channel']['members']     #then go through the memenbers
    for uid in members:
        guest = look_up_user(uid)
        if guest:
            dest = {"email": guest.email}    # if they have a different SL address then add that too
        else:
            gst_body = slack.getUser(uid)                                # get the users details
            dest = {"email":gst_body['user']['profile']['email']}       #mainly emai address
        starleafConference['participants'].append(dest)                # add to list odf invitees
    json_log(starleafConference,"STARLEAF CREATE")
    conf = star.createConf(starleafConference)
    try:
        dial = conf['dial_info']
    except:
        user.error = "KILL Failed to create conf"
        log("KILL failed to create SL conf")
        user.save()
        return
    
    url = data.get("response_url")
    uri = join.replace("<uri>",dial['dial_standards'])
    conf = uri.replace("<conf-id>",dial['access_code_pstn'])
    last = conf.replace("<url>",dial['dial_info_url'])
    post = last.replace("<uid>",name)
                               
    session = requests.Session()
    parms = json.dumps( {"text":post, "response_type": "in_channel"} )
    r = session.post(url,headers=headers,data=parms)

    if r.status_code != 200:
        user.error = "POST error "+str(r.status_code)
        user.save()
    log ( str(r.status_code)," KILL success")
    return


###############################################################################


@csrf_exempt
def slackpw(request):
    if request.method != 'POST':
        return HttpResponse("not accepted")
    email=data.get('email',"myemail")
    id=data.get('user_id',"nousr")
    pw =data.get('password',"wombat")
    user = look_up_user(user_id)
    if not user:
        user = make_user(user_id)
    user.password = pw
    user.email = email
    user.save()
    return HttpResponse("StarLeaf password set")


###############################################################################


@csrf_exempt
def slack(request):
    if request.method == 'POST':
        data = request.POST.copy()
    elif request.method == 'GET':
        data = request.GET.copy()
    else:
        HttpResponse("Failure")
    r = StarLeafSlack(data)
    return HttpResponse(r)





