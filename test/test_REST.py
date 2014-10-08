# -*- coding: utf-8 -*-
"""
Created on Thu Oct  2 17:05:00 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Testing REST module

"""

import sys
import json
import shlex
import logging
import unittest
import subprocess

#Adding library modules path
sys.path.append("..")

#IMporting REST.EndPoints
import REST.Config
import REST.EndPoints

class test_BaseEndPoint(unittest.TestCase):
    
    def setUp(self):
        """A test case to verify class assignment"""
        
        self.BaseEndPoint = REST.EndPoints.BaseEndPoint()
        
        
    def test_DefaultServerUP(self):
        """Test if default REST server is UP""" 
        
        status = self.BaseEndPoint.ping()
        self.assertTrue(status)
        
    def test_LocalServerUP(self):
        """Test if local server is UP"""
        
        BaseEndPoint = REST.EndPoints.BaseEndPoint(server="http://localhost:3000/")
        status = BaseEndPoint.ping()
        self.assertTrue(status)
        
    def test_RESTversion(self):
        version = self.BaseEndPoint.RESTversion()
        self.assertEqual(version, REST.Config.ENSEMBL_REST_VERSION)
        
    def test_APInDATAversions(self):
        """Testing if data and software versions are the same"""
        
        data = self.BaseEndPoint.DATAversions()
        api = self.BaseEndPoint.APIversion()
        self.assertEquals(data[0], api)
        
    def test_DATAversionisOne(self):
        """Testing the presence of ONE data version"""
        
        data = self.BaseEndPoint.DATAversions()
        self.assertEqual(len(data), 1)
    
    def test_RESTaction(self):
        """Testing a REST action with json data as POST content type"""
        
        #Check rest request via curl
        curl_cmd = """curl -H 'Accept: application/json' -H 'Content-type: application/json' --data '{ "ids" : ["rs116035550", "COSM476" ] }' http://rest.ensembl.org/vep/human/id/"""
        args = shlex.split(curl_cmd)
        curl = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        reference = json.load(curl.stdout)
        self.assertEqual(curl.wait(), 0)
        
        #check endopoint class
        test = self.BaseEndPoint.perform_rest_action(endpoint="vep/human/id/", json_msg='{ "ids" : ["rs116035550", "COSM476" ] }')
        self.assertEqual(reference, test)
        
        
#Doing tests
if __name__ == "__main__":
    #Logging istance
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

    #Adding docstring to test_BaseEndPoint.test_RESTversion
    test_BaseEndPoint.__dict__["test_RESTversion"].__doc__ = "Check if default server version is %s" %(REST.Config.ENSEMBL_REST_VERSION) 

    #doing tests
    unittest.main()
    


