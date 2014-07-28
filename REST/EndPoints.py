# -*- coding: utf-8 -*-
"""

Created on Tue Jul 15 15:02:15 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.it>

"""

import re
import json
import time
import types
import urllib
import logging
import urllib2
import StringIO
import Bio.SeqIO

from Config import ENSEMBL_ENDPOINTS, ENSEMBL_REST_SERVER, ENSEMBL_SUPPORTED_CODES

# Logger instance
logger = logging.getLogger(__name__)

# Setting the default logging level of this module
logger.setLevel(logging.WARN)

class RESTException(Exception):
    "Class for exception raised by REST server"

    def __init__(self, status, server):
        self.server = server
        self.status = status

        #checking if this status exists
        if ENSEMBL_SUPPORTED_CODES.has_key(status):
            self.name = ENSEMBL_SUPPORTED_CODES[status]["name"]
            self.notes = ENSEMBL_SUPPORTED_CODES[status]["notes"]

        else:
            self.name = "Unknown status"
            self.notes = "Unknown description"

    def __str__(self):
        return "REST server '%s' returned status %s (%s) : %s" %(self.server, self.status, self.name, self.notes)

class BaseEndPoint():
    """Base class for EnsEMBL REST class"""

    def __init__(self, server=ENSEMBL_REST_SERVER, reqs_per_sec=15):
        self.server = server
        self.reqs_per_sec = reqs_per_sec
        self.req_count = 0
        self.last_req = 0
        self._request = None
        self._response = None
        self._content = None
        self._info = None

    def perform_rest_action(self, endpoint, hdrs=None, params=None, json_msg=None):
        """Perform REST request with supplied params. Params can be a dictionary
        of optional parameters. json_msg is a json string passed by POST method"""
        if hdrs is None:
            hdrs = {}

        #Setting the default content type if not specified
        if 'Content-Type' not in hdrs:
            hdrs['Content-Type'] = 'application/json'

        logger.debug("Request Content-Type is '%s'" %(hdrs['Content-Type']))

        #Add additional params to endpoint
        if params:
            endpoint += '?' + urllib.urlencode(params)

        #The definitive request URL
        url = urllib.basejoin(self.server,endpoint)

        #this is the value returned by this function
        result = None

        # check if we need to rate limit ourselves
        if self.req_count >= self.reqs_per_sec:
            delta = time.time() - self.last_req
            if delta < 1:
                time.sleep(1 - delta)
            self.last_req = time.time()
            self.req_count = 0

        try:
            #debug
            logger.info("Performing request to '%s' json_data='%s'" %(url, json_msg))

            #If data != None urllib2 will use a POST method
            request = urllib2.Request(url, data=json_msg, headers=hdrs)
            self._request = request

            response = urllib2.urlopen(request)
            self._response = response

            content = response.read()
            self._content = content

            #Setting request and response values for debugging
            self._info = response.info()

            #Cheking response
            #TODO: return content type defined by the user, do not parse results at this point
            if content:
                if self._info['content-type'] == 'application/json':
                    result = json.loads(content)

                elif self._info['content-type'] == "text/x-fasta":
                    handle = StringIO.StringIO(content)
                    result = Bio.SeqIO.read(handle, "fasta")

                else:
                    result = content

            #Increasing request counter by one
            self.req_count += 1

            #checking if this client has been rate limited
            if self._info.has_key("x-ratelimit-remaining"):
                logger.warning("This client has been rate-limited by '%s'" %(self.server))
                logger.warning("You have %s requests left" %(self._info["x-ratelimit-remaining"]))
                logger.warning("Counter will be resetted in %s seconds (%s)" %(self._info["x-ratelimit-reset"], time.ctime(time.time()+float(self._info["x-ratelimit-reset"]))))

        #For 200 error codes, the response object is returned immediately, else I will find an exception
        except urllib2.HTTPError, e:
            # check if we are being rate limited by the server
            if e.code == 429 and 'Retry-After' in e.headers:
                retry = e.headers['Retry-After']
                logger.warning("You've been rate-limited. Waiting %s secs..." %(retry))
                time.sleep(float(retry))
                self.perform_rest_action(endpoint, data=json_msg, headers=hdrs)

            else:
                logger.critical('Request failed for {0}: Status code: {1.code} Reason: {1.reason}\n'.format(endpoint, e))
                #throw my "useful exception"
                raise RESTException(status=e.code, server=self.server)

        except urllib2.URLError, e:
            # testing if server is up
            if not self.ping():
                logger.error("Server %s seems to be down" %(self.server))

            #raising in any case an exception
            raise urllib2.URLError, e

        return result

    def ping(self, endpoint='/info/ping'):
        """Return True if server is UP"""

        logger.debug("Testing if EnsEMBL server is active")

        #I can't call perform rest action, because in that function I want to determine if server is up with this function
        url = urllib.basejoin(self.server, endpoint)
        request = urllib2.Request(url, headers={'Content-Type' : 'application/json'})

        try:
            response = urllib2.urlopen(request)
            content = response.read()
            data = json.loads(content)

            if data == {u'ping': 1}:
                logger.info("EnsEMBL REST server is UP")
                return True

            else:
                logger.critical("EnsEMBL REST server is DOWN")
                return False

        except urllib2.URLError, e:
            logger.critical("%s returned :%s" %(endpoint, e.args))
            return False

class EnsEMBLEndPoint(BaseEndPoint):
    def __init__(self, server=ENSEMBL_REST_SERVER, reqs_per_sec=15):
        """The main class for all EnsEMBL REST endpoints"""

        #Base class initialization
        BaseEndPoint.__init__(self, server, reqs_per_sec)

        # register available functions to allow listing name when debugging
        def regFunc(key, endpoint_params):
            return lambda **kwargs: self.__genericFunction(key, endpoint_params, **kwargs)

        for function, params in ENSEMBL_ENDPOINTS.iteritems():
            self.__dict__[function] = regFunc(function, params)

            #Set __doc__ for generic function
            if params.has_key("description"):
                #Add a docstring to lambda function to get help on that function
                self.__dict__[function].__doc__ = params["description"]
                self.__dict__[function].__name__ = function


    def __genericFunction(self, api_call, endpoint_params, **kwargs):
        #Verify required variables and raise an Exception if needed
        mandatory_params = re.findall('\:(?P<m>\w+)', endpoint_params['url'])

        logger.debug("Verifing mandatory parameters...")

        #TODO: check those mandatory parameters againts config file

        for param in mandatory_params:
            if not kwargs.has_key(param):
                raise Exception, "%s requires %s as mandatory params" %(api_call, mandatory_params)

        logger.debug("Checking additional parameters...")

        #Setting json_msg (will have a value only for POST methods)
        json_msg = None

        #TODO: Setting user defined content type or the default content type

        #Setting default content type for this method
        headers = {'Content-Type': endpoint_params['default_content_type']}

        #the post method has a special parameter
        if endpoint_params['method'] == 'POST':
            logger.debug("Cheking POST message...")

            if not kwargs.has_key(endpoint_params['message_param']):
                logger.critical("%s must have %s parameter to get data via POST method" %(api_call, endpoint_params['message_param']))
                raise Exception, "Error in %s: %s parameter is mandatory" %(api_call, endpoint_params['message_param'])

            #in endpoint_params['message_param'] there's the key in which input data are
            json_msg = kwargs[endpoint_params['message_param']]

            #Ensuring that json_msg is a string
            if type(json_msg) != types.StringType:
                try:
                    json_msg = json.dumps(json_msg)

                except Exception, message:
                    logger.critical("%s %s parameter has to be a json string or an object to be converted in json string" %(api_call, endpoint_params['message_param']))
                    raise Exception, message

            del(kwargs[endpoint_params['message_param']])

            #Setting the json Accept content type (json for POST methods is mandatory)
            headers['Accept'] = "application/json"

            #Checking Content-Type of Response
            if headers['Content-Type'] != "application/json":
                logger.error("%s response 'Content-Type' seems to be '%s' . However EnsEMBL will reply in 'application/json'" %(api_call, headers['Content-Type']))


        #define non mandatory params to perform rest_action. Start
        additional_params = {}

        for param, value in kwargs.iteritems():
            if param in endpoint_params['optional_params']:
                additional_params[param] = value

            elif param not in mandatory_params:
                logger.warn("Ignoring %s = %s" %(param, value))

        #make endpoint URL
        endpoint = re.sub('\:(?P<m>\w+)', lambda m: "%s" %(kwargs.get(m.group(1))), endpoint_params['url'])

        return self.perform_rest_action(endpoint, hdrs=headers, params=additional_params, json_msg=json_msg)

