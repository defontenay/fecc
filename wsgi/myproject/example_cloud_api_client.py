import requests

session = requests.Session()
url='http://127.0.0.1:8000/poll'
#url='http://fecc-codian.rhcloud.com/poll'
print "getting ",url
while True:
    response = session.get(url)
    body = response.text
    print body





