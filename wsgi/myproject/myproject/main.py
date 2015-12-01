
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

apiServer='https://portal.starleaf.com/v1'


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
    return  HttpResponse(page)

###############################################################################

def getBluejeansURI(description):
    match = re.search('Enter Meeting ID: ([0-9]{9,18})\s', description)
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
        if "static" in LOGFILE:
            data = json.loads(request.body)
        else:
            data = request.POST.copy()
        att = data.get('attachments',0)
        env  = json.loads(data['envelope'])
        sub = data.get('subject',"*****")
        string = " attachments: "+ " subject: "+sub
        log(string)
        json_log(env,"ENVELOPE")
        if att > 0:
            info = json.loads(data.get('attachment-info'))
            json_log(info,"ATTCHMENTS")
            for x in range(1,att+1):
                name = "attachment"+str(x)
                file = info[name]
                if "ics" in file['type']:
                    ics = data.get(name)
                    break;

            log ("found an ICS .... "+file['name']+" size "+str(len(ics)))


        cal = Calendar.from_ical(ics)
        method = cal['METHOD'] #       if method not in ['REQUEST', 'CANCEL']:

        for event  in cal.walk():
            if event.name == "VEVENT":
                uri = None
                if "bluejeans" in env["from"]:
                    uri = getBlueJeansURI(event.get('DESCRIPTION'))
                if "webex" in env["from"]:
                    uri = getWebexURI(event.get('DESCRIPTION'))
                if uri == None:
                    uri = getGenericURI(event.get('DESCRIPTION'))
                if uri == None:
                      return HttpResponse("No URI found")
                
                settings = {
                        'title':event.get('SUMMARY'),
                        'permanent': False,
                        'participants': [{'email':env['to'][0]}],
                        'timezone': getTimezone(event.decoded('DTSTART').tzinfo.zone),
                        'start': event.decoded('DTSTART').replace(tzinfo=None).isoformat(),
                        'end': event.decoded('DTEND').replace(tzinfo=None).isoformat(),
                        'uri': uri,
                        }
                json_log(settings)
        star = StarLeafClient(username="wmm+185@starleaf.com",password="wombat",apiServer=apiServer)
        star.authenticate()
        if method == 'REQUEST':
            star.deleteGreenButton(uri)
            star.createGreenButton(settings)
        else:
            star.deleteGreenButton(uri)

    except Exception, e:
        log ("EXCEPTION:  ", e.message)
        return  HttpResponse(e.message)
    return HttpResponse()

###############################################################################

def log(logdata,header=""):
    log = open(LOGFILE, 'a')
    log.write(str(datetime.datetime.now())+"--------------------\n")
    log.write (header)
    if "static" in LOGFILE:
        print logdata, header
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












