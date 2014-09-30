# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 10:17:27 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A series of function to deal with snpchim database

"""

import MySQLdb
import ConfigParser

class configException(Exception): pass

class Config(ConfigParser.ConfigParser):
    """A class to deal with Config file"""
    def __init__(self, configfile="/var/www/.snpchimp2_conf.ini"):        
        #Read the global ini file with database credentials
        ConfigParser.ConfigParser.__init__(self)
        self.read(configfile)
        
    #some methods to get useful data from Config file
    def getAllowedAnimals(self):
        """Return a dictionary of allowed animals in a config file"""
        
        return dict((k,v) for k,v in self.items("allowed_animals"))
    
    def getAssembliesByAnimal(self, animal):
        """Return a dictionary of allowed assemblies giving an animal"""
            
        if animal not in self.getAllowedAnimals().keys():
            raise configException, "I couldn't find %s_assemblies in config file" %(animal)
            
        return dict((k,v) for k,v in self.items("%s_assemblies" %(animal)))

class snpchimpDBException(Exception): pass

class SNPchiMp2():
    """A class top deal with snpchimp database"""
    
    def __init__(self):
        self.config = Config()
        self.host = self.config.get("database","host")
        self.user = self.config.get("database","usr")
        self.passwd = self.config.get("database","pwd")
        self.db = self.config.get("database","db")
        
        #Which db parameters are specified as class attributes
        self.__parameters = ["host", "user", "passwd", "db"]
        
        #a variable in which store connections
        self.__connection = None
        
        #Which animals are allowed
        self.allowed_animals = self.config.getAllowedAnimals()
        
    def getConnection(self, **kwargs):
        """Return a MySQLdb connection to database. With no parameters, the default
        database specified .ini file will be opened. Optionally you could define 
        yours host, user, passws and db parameters"""
        
        #override the default parameters, if specified
        for k,v in kwargs.iteritems():
            if k not in self.__parameters:
                raise snpchimpDBException, "%s is not a valid parameters. Valid parameters are %s" %(k, self.__parameters)
            setattr(self, k, v)
            
        #get a (new) mysqldb connection
        if self.__connection == None or len(kwargs) > 0:
            self.__connection = MySQLdb.connect(host=self.host, passwd=self.passwd, user=self.user, db=self.db)
            
        #return a connection to database
        return self.__connection
        
    
        
    