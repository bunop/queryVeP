# -*- coding: utf-8 -*-
"""

Created on Tue Jul 15 15:02:15 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.it>

"""

import re
import sys
import json
import time
import types
import urllib
import logging
import urllib2

from Config import ENSEMBL_ENDPOINTS, ENSEMBL_REST_SERVER

#Logger instance
logger = logging.getLogger(__name__)

class BaseEndPoint():
    """Base class for EnsEMBL REST class"""
    def __init__(self, server=ENSEMBL_REST_SERVER, reqs_per_sec=15):
        self.server = server
        self.reqs_per_sec = reqs_per_sec
        self.req_count = 0
        self.last_req = 0

    def perform_rest_action(self, endpoint, hdrs=None, params=None, json_msg=None):
        """Perform REST request with supplied params. Params can be a dictionary
        of optional parameters. json_msg is a json string passed by POST method"""
        if hdrs is None:
            hdrs = {}

        #Setting the default content type if not specified
        if 'Content-Type' not in hdrs:
            hdrs['Content-Type'] = 'application/json'

        logger.debug("Request %s Content-Type" %(hdrs['Content-Type']))

        #Add additional params to endpoint
        if params:
            endpoint += '?' + urllib.urlencode(params)

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
            #If data != None urllib2 will use a POST method
            request = urllib2.Request(self.server + endpoint, data=json_msg, headers=hdrs)
            response = urllib2.urlopen(request)
            content = response.read()
            if content:
                result = json.loads(content)
            self.req_count += 1

        #TODO: Fix that function
        except urllib2.HTTPError, e:
            # check if we are being rate limited by the server
            if e.code == 429:
                if 'Retry-After' in e.headers:
                    retry = e.headers['Retry-After']
                    time.sleep(float(retry))
                    self.perform_rest_action(self.server + endpoint, data=json_msg, headers=hdrs)
            else:
                sys.stderr.write('Request failed for {0}: Status code: {1.code} Reason: {1.reason}\n'.format(endpoint, e))

        return result

    def ping(self, endpoint='/info/ping'):
        """Testing if server is UP"""

        logger.debug("Testing if EnsEMBL server is active")

        if self.perform_rest_action(endpoint) == {u'ping': 1}:
            logger.info("EnsEMBL REST server is UP")

        else:
            logger.critical("EnsEMBL REST server is DOWN")

class Variation(BaseEndPoint):
    def __init__(self):
        #Base class initialization
        BaseEndPoint.__init__(self)

        # register available functions to allow listing name when debugging
        def regFunc(key, endpoint_params):
            return lambda **kwargs: self.__genericFunction(key, endpoint_params, **kwargs)

        for function, params in ENSEMBL_ENDPOINTS["Variation"].iteritems():
            self.__dict__[function] = regFunc(function, params)

            #Set __doc__ for generic function
            if params.has_key("description"):
                self.__dict__[function].__doc__ = params["description"]


    def __genericFunction(self, api_call, endpoint_params, **kwargs):

        #Verify required variables and raise an Exception if needed
        mandatory_params = re.findall('\:(?P<m>\w+)', endpoint_params['url'])

        logger.debug("Verifing mandatory parameters...")

        for param in mandatory_params:
            if not kwargs.has_key(param):
                raise Exception, "%s requires %s as mandatory params" %(api_call, mandatory_params)

        logger.debug("Checking additional parameters...")

        json_msg = None

        #the post method has a special parameter
        if endpoint_params['method'] == 'POST':
            logger.debug("Cheking POST message")

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

        #define non mandatory params to perform rest_action. Start
        additional_params = {}

        for param, value in kwargs.iteritems():
            if param in endpoint_params['optional_params']:
                additional_params[param] = value

            else:
                logger.warn("Ignoring %s = %s" %(param, value))

        #make endpoint URL
        endpoint = re.sub('\:(?P<m>\w+)', lambda m: "%s" %(kwargs.get(m.group(1))), endpoint_params['url'])

        #Setting default content type for this method
        headers = {'Content-Type': endpoint_params['default_content_type']}

        logger.debug("Performing request to '%s' endpoint" %(self.server+endpoint))

        return self.perform_rest_action(endpoint, hdrs=headers, params=additional_params, json_msg=json_msg)

