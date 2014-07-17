# -*- coding: utf-8 -*-
"""

Created on Tue Jul 15 15:02:15 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.it>

"""

import re
import sys
import json
import time
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
        
    def perform_rest_action(self, endpoint, hdrs=None, params=None):
        if hdrs is None:
            hdrs = {}

        if 'Content-Type' not in hdrs:
            hdrs['Content-Type'] = 'application/json'

        if params:
            endpoint += '?' + urllib.urlencode(params)

        data = None

        # check if we need to rate limit ourselves
        if self.req_count >= self.reqs_per_sec:
            delta = time.time() - self.last_req
            if delta < 1:
                time.sleep(1 - delta)
            self.last_req = time.time()
            self.req_count = 0

        try:
            request = urllib2.Request(self.server + endpoint, headers=hdrs)
            response = urllib2.urlopen(request)
            content = response.read()
            if content:
                data = json.loads(content)
            self.req_count += 1

        #TODO: Fix that function
        except urllib2.HTTPError, e:
            # check if we are being rate limited by the server
            if e.code == 429:
                if 'Retry-After' in e.headers:
                    retry = e.headers['Retry-After']
                    time.sleep(float(retry))
                    self.perform_rest_action(endpoint, hdrs, params)
            else:
                sys.stderr.write('Request failed for {0}: Status code: {1.code} Reason: {1.reason}\n'.format(endpoint, e))

        return data
        
    def ping(self, endpoint='/info/ping'):
        """Testing if server is UP"""
        
        logger.debug("Testing if EnsEMBL server is active")
        
        return self.perform_rest_action(endpoint)
        
class Variation(BaseEndPoint):
    def __init__(self):
        #Base class initialization
        BaseEndPoint.__init__(self)
    
        # register available functions to allow listing name when debugging
        def regFunc(key, endpoint_params):
            return lambda **kwargs: self.__genericFunction(key, endpoint_params, **kwargs)
            
        for function, params in ENSEMBL_ENDPOINTS["Variation"].iteritems():
            self.__dict__[function] = regFunc(function, params)
        
    
    def __genericFunction(self, api_call, endpoint_params, **kwargs):
        
        #TODO: Verify required variables and raise an Exception if needed
        #TODO: Set __doc__ for generic function        
        
        #make endpoint URL
        endpoint = re.sub('\:(?P<m>\w+)', lambda m: "%s" %(kwargs.get(m.group(1))), endpoint_params['url'])
        
        return self.perform_rest_action(endpoint)
        
