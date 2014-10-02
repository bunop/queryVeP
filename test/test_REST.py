# -*- coding: utf-8 -*-
"""
Created on Thu Oct  2 17:05:00 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Testing REST module

"""

import sys
import logging
import unittest

#Adding library modules path
sys.path.append("..")

#IMporting REST.EndPoints
import REST.Config
import REST.EndPoints

class test_BaseEndPoint(unittest.TestCase):
    def setUp(self):
        """A test case to verify class assignment"""
        
        self.BaseEndPoint = REST.EndPoints.BaseEndPoint()
        self.version = u'3.0.0'
        
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
        version = self.BaseEndPoint.version()
        self.assertEqual(version, self.version)
        
#Doing tests
if __name__ == "__main__":
    #Logging istance
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

    #Adding docstring to test_BaseEndPoint.test_RESTversion
    test_BaseEndPoint.__dict__["test_RESTversion"].__doc__ = "Check if default server version is %s" %(REST.Config.ENSEMBL_REST_VERSION) 

    #doing tests
    unittest.main()
    


