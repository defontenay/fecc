
import json
import requests
import datetime
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from settings import LOGFILE, STATIC_ROOT


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

###############################################################################

def serve_blank(request):
    return  HttpResponse(page)

@csrf_exempt
def email(request):
    
    log ("","New email received")
    if request.method != 'POST':
        return HttpResponse('Invalid method')
    
    try:
        data = request.GET.copy()
        att = data.get('attachments')
        fr = data.get('from')
        sub = data.get('subject')
        too =data.get('to')
        log(request.body," whole body")


    except Exception, e:
        print "Exception"
        print e.message
        return  HttpResponse(e.message)
    return HttpResponse()

def log(logdata,header=""):
    log = open(LOGFILE, 'a')
    log.write(str(datetime.datetime.now())+"  "+header+" ---------------------------------\n")
    if "static" in LOGFILE:
        print "------------",header
        print logdata
    log.write(logdata)
    log.write("\n")
    log.close()
    return 0
    
    














