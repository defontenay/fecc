
import requests
import json
import random
from  time import sleep
import datetime
import threading
import socket
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET



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
flag = threading.Event()


HOST = '127.0.0.1'      # Symbolic name meaning the local host
PORT = 50007            # Arbitrary non-privileged port
addr = None
conn = None


def listener():
    global addr, conn
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    running = True

    print "Hello world"

    while running:
        print "Waiting for connection"
        conn, addr = s.accept()
        print 'Connected by', addr
        try:
            data = conn.recv(1024)
        except:
            print "excepyion"
            conn.close()
        print "done"
        addr = None

thread = threading.Thread(target=listener)
thread.start()

###############################################################################
def serve_poll(request):
    global set_var
    if set_var == ".":
        flag.wait(5.3)
    response = set_var
    set_var = "."
    flag.clear()
    return HttpResponse(response)

##############################################################################

def perform(command):
    global set_var
    if addr != None:
        conn.send(command)
    set_var = command
    flag.set()
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














