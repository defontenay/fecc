
import json
import re
import requests
import datetime
from icalendar import Calendar, Event
from icalendar.prop import vBinary, vBoolean, vCalAddress, vDatetime, vDate, \
            vDDDTypes, vDuration, vFloat, vInt, vPeriod, \
            vWeekday, vFrequency, vRecur, vText, vTime, vUri, \
            vGeo, vUTCOffset, TypesFactory
import pytz
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from settings import LOGFILE, STATIC_ROOT
from starleaf import StarLeafClient
from slack import StarLeafSlack

apiServer='https://portal.starleaf.com/v1'
username="wmm+185@starleaf.com"
password="wombat"


page = '<!DOCTYPE html> \
<html> \
<body>\
<p>Click the buttons</p> \
<table>\
\
<tr>\
<td> </td> \
<td> <form method="get" action="/up"> <button type="submit">UP</button></form> </td>  \
<td> </td> \
</tr> \
\
<tr> \
<td> <form method="get" action="/left"> <button type="submit">LEFT</button></form> </td> \
<td> </td>  \
<td> <form method="get" action="/right"> <button type="submit">RIGHT</button></form> </td> \
</tr> \
\
<tr>\
<td> </td> \
<td> <form method="get" action="/down"> <button type="submit">DOWN</button></form> </td>  \
<td> </td> \
</tr> \
\
<tr>\
<td> </td> \
<td> ......... </td>  \
<td> </td> \
</tr> \
\
<tr> \
<td> <form method="get" action="/in"> <button type="submit">IN</button></form> </td> \
<td> <form method="get" action="/pc"> <button type="submit">PC</button></form> </td> \
<td> <form method="get" action="/out"> <button type="submit">OUT</button></form> </td> \
</tr> \
\
\
\
</table>\
</body>\
</html> '

set_var = "."


###############################################################################

###############################################################################
def serve_poll(request):
    global set_var
    response = set_var
    set_var = "."
    return HttpResponse(response)

##############################################################################

def perform(command):
    global set_var
    set_var = command
    return

def left(request):
    perform ("LEFT")
    return HttpResponse(page)

def right(request):
    perform ("RIGHT")
    return HttpResponse(page)

def up(request):
    perform ("UP")
    return HttpResponse(page)

def down(request):
    perform ("DOWN")
    return HttpResponse(page)

def zin(request):
    perform ("IN")
    return HttpResponse(page)

def out(request):
    perform ("OUT")
    return HttpResponse(page)

def pc(request):
    perform ("PC")
    return HttpResponse(page)

def serve_blank(request):
    print "Got Request"
    return  HttpResponse(page)

###############################################################################

def getBlueJeansURI(description):
    match = re.search('Enter Meeting ID: ([0-9]{9,18}?)\s', description)
    print "description ",match
    print description
    if not match:
        return None
    return match.group(1) + '@bjn.vc'


def getWebexURI(description):
    match = re.search('sip:([0-9]{9,18}@[a-zA-Z0-9-.]{0,62}?)\s', description)
    if not match:
        return None
    return match.group(1)


def getGenericURI(description):
    match = re.search('sip:\s*([0-9]{9,18}@[a-zA-Z0-9-.]{0,62}?)\s', description)
    if match:
        return match.group(1)
    match = re.search('([0-9]{4,18}@[a-zA-Z0-9-.]{0,62}?)\s', description)
    if match:
        return match.group(1)
    match = re.search('sip:([a-zA-Z0-9-.+_]{4,64}@[a-zA-Z0-9-.]{0,62}?)\s', description)
    if match:
        return match.group(1)
    return None

#Skype Meeting<https://meet.lync.com/starleaf1/william.macdonald/03ZIU1XF>

def getLyncURI(description,email):
    match = re.search('[a-zA-Z0-9-.+_]{4,64}@([a-zA-Z0-9-.]{0,62}?)',email)
    if not match:
        return None
    dom = match.group(1)
    return None
#    match = re.search('Meeting<https://meet.lync.com/[a-zA-Z0-9-._]{0,62}/([a-zA-Z0-9-._]{0,62})/[a-zA-Z0-9-._]{0,16})>',description)



def getTimezone(timezone):
    if timezone == 'GMT':
        timezone = 'Europe/London'
    try:
        pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        TZ = timezone.upper()
        if "EASTERN" in TZ:
            return "America/New_York"
        if "PACIFIC" in TZ:
            return "America/Los_Angeles"
        if "MOUNTAIN" in TZ:
            return "America/Denver"
        if "CENTRAL" in TZ:
            return "America/Detroit"
        if "WESTERN" in TZ:
            return "Europe/London"
    return timezone

@csrf_exempt
def email(request):
    
    log ("New email received")
                      
    if request.method != 'POST':
        return HttpResponse('Invalid method')
            
    try:
        data = request.POST.copy()
        att = data.get('attachments',0)
        env  = json.loads(data['envelope'])
        sub = data.get('subject',"*****")
        to = data.get('to',"")
        cc = data.get('cc',"")
        log (to,"TO ")
        log (cc,"CC ")
        ics = None
        att = int(att)
        if request.FILES:
            for f in request.FILES:
                log (f, "FILE")
        json_log(env,"ENVELOPE")
        if att == 0:
            log (data,"BODY (no attachments)")
        else:
            info = json.loads(data.get('attachment-info'))
            json_log(info,"ATTCHMENTS")
            for x in range(1,att+1):
                log (str(x))
                name = "attachment"+str(x)
                log (name)
                file = info[name]
                json_log(file,"FILE")
                if 'filename' in file and ".ics" in file['filename']:
                    ics_file = request.FILES.get(name)
                    print name," ... ",ics_file
                    ics = ics_file.read()
                    print ics
                    break;


        if not ics:
            if request.FILES:
                for f in request.FILES:
                    log(f,"FILES")
            return HttpResponse("no ICS")

        log ("found an ICS .... "+file['name']+" size "+str(len(ics)))

        cal = Calendar.from_ical(ics)
        method = cal['METHOD'] #       if method not in ['REQUEST', 'CANCEL']:

        for event  in cal.walk():
            if event.name == "VEVENT":
                uid = event.get('UID')
                log ( uid, "UID" )
                

                uri = None
                if method == 'REQUEST':
                    if "bluejeans" in env["from"]:
                        uri = getBlueJeansURI(event.get('DESCRIPTION'))
                    if "webex" in env["from"]:
                        uri = getWebexURI(event.get('DESCRIPTION'))
                    if uri == None:
                        uri = getGenericURI(event.get('DESCRIPTION'))
                    if uri == None:
                        return HttpResponse("No URI found")
                
                    participants = []
                    ems = re.findall(r'([a-zA-Z0-9-.+_]{1,64}@[a-zA-Z0-9-.]{3,62})', to)
                    for em in ems:
                        participants.append( {'email':em} )
                    ems = re.findall(r'([a-zA-Z0-9-.+_]{1,64}@[a-zA-Z0-9-.]{3,62})', cc)
                    for em in ems:
                        participants.append( {'email':em} )

                    settings = {
                        'title':event.get('SUMMARY'),
                        'permanent': False,
                        'participants': participants,
                        'timezone': getTimezone(event.decoded('DTSTART').tzinfo.zone),
                        'start': event.decoded('DTSTART').replace(tzinfo=None).isoformat(),
                        'end': event.decoded('DTEND').replace(tzinfo=None).isoformat(),
                        'uri': uri,
                        }
                    json_log(settings,"SL-SETTINGS")

                    star = StarLeafClient(username=username,password=password,apiServer=apiServer)
                    star.authenticate()
                    star.deleteGreenButton(uid)
                    star.createGreenButton(settings,uid)
                else:
                    star = StarLeafClient(username=username,password=password,apiServer=apiServer)
                    star.authenticate()
                    star.deleteGreenButton(uid)
                break;

    except Exception, e:
        log ("EXCEPTION:  ", e.message)
        return  HttpResponse("EXECPTION is  "+e.message)
    return HttpResponse("Success")

###############################################################################

def slack(request):
    
    if request.method == 'POST':
        data = request.POST.copy()
    elif request.method == 'GET':
        data = request.GET.copy()
    else:
        HttpResponse("Failure")
    log ("REQUEST FROM SLACK")
    r = StarLeafSlack(data)
    log(r,"BACK TO SLACK\n")
    return HttpResponse(r)


###############################################################################

def log(logdata,header=""):
    log = open(LOGFILE, 'a')
    log.write(str(datetime.datetime.now())+"--------------------\n")
    log.write (header)
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
    log.write(str(datetime.datetime.now())+"--------------------\n")
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












