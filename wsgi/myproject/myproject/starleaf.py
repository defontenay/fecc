

import requests
import json
import hashlib
import hmac
import re
import pbkdf2
import binascii
import pytz
import time
import warnings

headers = {'Content-type': 'application/json'}

class StarLeafClient(object):
    """
        This is a client implementing the StarLeaf Cloud API Version 1.
        """
    
    # The address of the API server should be passed into the constructor,
    # if different from the default.
    
    
    def __init__(self, username, password,  apiServer, sslVerify=False):
        self.apiServer = apiServer
        self.username = username
        self.password = password
        self.sslVerify = sslVerify
        self.key = None
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
            txt_log ("SL Need to authenticate")
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
        txt_log ('SL Response code is:' + str(response.status_code))
        try:
            body = response.json()
        except ValueError:
            return None
        else:
            json_log (body)
            return body

    def _apiAuthentication(self, salt_hex, iterations, challenge_hex):
        if self.key is None:
            salt = binascii.unhexlify(salt_hex)
            self.key = pbkdf2.PBKDF2(passphrase=self.password, salt=salt,
                                     iterations=iterations, digestmodule=hashlib.sha256,
                                     macmodule=hmac).read(32)
                
        challenge = binascii.unhexlify(challenge_hex)
        _hash = hmac.new(self.key, challenge, hashlib.sha256)
        response = _hash.hexdigest()
        return response

    def authenticate(self):
        params = {'username': self.username}
        body = self._get('/challenge', params=params)
            
        if body is not None:
            authResponse = self._apiAuthentication(body['salt'],
                                                       body['iterations'],
                                                       body['challenge'])
            postBody = { 'username': self.username,
                        'response': authResponse}
            txt_log ('SL Sending challenge response to API server.')
            body = self._post('/authenticate', postBody)
            if body and "error" in body:
                return None
        return body

    def createGreenButton(self, settings, confId):
            postBody = {'settings': settings}
            url = self.apiServer + "/myconferences/" + confId
            txt_log ("url is  "+url)
            json_log(settings)
            try:
                r = self.session.put(url, data=json.dumps(postBody), headers=headers, verify=self.sslVerify)
                self._getBody(r)
            except Exception as e:
                txt_log ("Cloud API error "+e.message)


    def deleteGreenButton(self, confId):
            url = self.apiServer + "/myconferences/" + confId
            txt_log ("url is  "+url)
            try:
                r = self.session.delete(self.apiServer + "/myconferences/" + confId, verify=self.sslVerify)
                self._getBody(r)
            except Exception as e:
                txt_log ("Cloud API error"+e.message)


    def createConf(self, settings):
        print('Creating conference.')
        postBody = {'settings': settings}
        respBody = self._post('/myconferences', postBody)
        if respBody is not None and respBody.get('conf_id') is not None:
            print('New conference created with id: %s' % respBody['conf_id'])
        return respBody

    def updateConf(self, confId, settings):
        print('Changing conference with id: %s' % confId)
        postBody = {'settings': settings}
        self._put('/myconferences/%s' % confId, postBody)

    def deleteConf(self, confId):
        print('Deleting conference with id: %s' % confId)
        self._delete('/myconferences/%s' % confId)

    def getConf(self, confId):
        print('Getting conference info with id: %s' % confId)
        return self._get('/myconferences/%s' % confId)




###############################################################################
def txt_log(logdata):
        print logdata


###############################################################################
def json_log(logdata):
        print json.dumps(logdata, sort_keys=True, indent=4, separators=(',', ': '))

warnings.filterwarnings("ignore")
