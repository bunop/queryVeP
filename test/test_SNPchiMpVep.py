#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 10:44:02 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

testing test_SNPchiMpVep.py with sample data

"""

import os
import cgi
import cgitb
import urllib
import urllib2
import unittest

animal = 'cow'
assembly = 'umd3'
vep_input_string = '1:516404:Hapmap53946-rs29015852,1:516404:Hapmap53946-rs29015852,1:516404:Hapmap53946-rs29015852,1:516404:Hapmap53946-rs29015852,1:516404:Hapmap53946-rs29015852,1:516404:Hapmap53946-rs29015852,1:516404:Hapmap53946-rs29015852,1:516404:Hapmap53946-rs29015852,1:516404:Hapmap53946-rs29015852,1:822710:BovineHD4100000005,1:434180:BTA-07251-no-rs,1:434180:BTA-07251-no-rs,1:135098:Hapmap43437-BTA-101873,1:135098:Hapmap43437-BTA-101873,1:135098:Hapmap43437-BTA-101873,1:135098:Hapmap43437-BTA-101873,1:135098:Hapmap43437-BTA-101873,1:135098:Hapmap43437-BTA-101873,1:135098:Hapmap43437-BTA-101873,1:135098:Hapmap43437-BTA-101873,1:135098:Hapmap43437-BTA-101873,1:517814:BovineHD4100000003,1:506410:BovineHD4100000002,1:522543:BovineHD4100000004,1:393248:Hapmap34944-BES1_Contig627_1906'

#create data like a dictionary
data = dict(animal=animal, assembly=assembly, vep_input_string=vep_input_string)
params = urllib.urlencode(data)
url = "http://nginx:20080/queryVeP/SNPchiMpVep.py"

#Setting headers
headers = {}

#debug
if os.environ.has_key("HTTP_USER_AGENT"):
    #Warning: These techniques expose information that can be used by an attacker. Use it only while developing/debugging. Once in production disable them.
    cgitb.enable()

    #To open this output with a browser
    print("Content-type: text/html\n")

    #debug
    #cgi.test()

#    print json_msg
#    print headers
#    print params

#This type of request is a POST request. Is the same of
#curl --data 'animal=cow&assembly=umd3&vep_input_string=1:516404:Hapmap53946-rs29015852' "http://localhost:10080//cgi-bin/pyEnsEMBLrest/SNPchiMpVep.py"
#see http://curl.haxx.se/docs/httpscripting.html#POST tutorial for details
if __name__ == "__main__":
    request = urllib2.Request(url, data=params)
    response = urllib2.urlopen(request)

    #print response.info()

    content = response.read()

    print content
