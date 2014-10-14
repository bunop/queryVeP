# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 10:17:27 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A series of function to deal with snpchim database

"""

import logging
import MySQLdb
import ConfigParser

# Logger instance
logger = logging.getLogger(__name__)

class configException(Exception): pass

class Config(ConfigParser.ConfigParser):
    """A class to deal with Config file"""
    def __init__(self, configfile="/var/www/.snpchimp2_conf.ini"):        
        #Read the global ini file with database credentials
        ConfigParser.ConfigParser.__init__(self)
        
        logger.debug("reading configfile %s" %(configfile))
        self.read(configfile)
        
    #some methods to get useful data from Config file
    def getAllowedAnimals(self):
        """Return a dictionary of allowed animals in a config file"""
        
        return dict((k,v) for k,v in self.items("allowed_animals"))
    
    def getAssembliesByAnimal(self, animal):
        """Return a dictionary of allowed assemblies giving an animal"""
            
        if animal not in self.getAllowedAnimals().keys():
            raise configException, "I couldn't find '%s_assemblies' in config file" %(animal)
            
        return dict((k,v) for k,v in self.items("%s_assemblies" %(animal)))

class snpchimpDBException(Exception): pass

class SNPchiMp2():
    """A class top deal with snpchimp database"""
    
    def __init__(self,configfile="/var/www/.snpchimp2_conf.ini"):
        self.config = Config(configfile)
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
                raise snpchimpDBException, "'%s' is not a valid parameters. Valid parameters are %s" %(k, self.__parameters)
            
            logger.info("Setting 'self.%s' to '%s' " %(k,v))
            setattr(self, k, v)
            
        #get a (new) mysqldb connection
        if self.__connection == None or len(kwargs) > 0:
            logger.debug("Connecting to database '%s' on host '%s'" %(self.db, self.host))
            self.__connection = MySQLdb.connect(host=self.host, passwd=self.passwd, user=self.user, db=self.db)
            
        #return a connection to database
        return self.__connection
        
    def getVariants(self, animal, assembly, vep_input_data):
        """Query SNPchiMp2 database, using animal and assembly to identify the
        correct table. vep_input_data must derive from downloadSNP.php call from
        snpchimp, ad parsed by the parseVePinput of the helper script"""
        
        #check if animal is allowed
        if animal not in self.allowed_animals.keys():
            raise snpchimpDBException, "Animal %s isn't in %s database" %(animal, self.db)
            
        #Check assembly if exists
        assemblies = self.config.getAssembliesByAnimal(animal)
        
        if assembly not in assemblies.keys():
            raise snpchimpDBException, "Assembly '%s' isn't in '%s' database. Assemblies are %s" %(assembly, self.db, assemblies.keys())
        
        #TODO: check correctness of vep_input_data
        logger.info("%s variants received in input" %(len(vep_input_data)))
        
        #derive the correct table
        prefix = self.allowed_animals[animal]
        suffix = assemblies[assembly]
        table = "%s_join_%s" %(prefix, suffix)
        
        #no "." are in table. Correct table name
        table = table.replace(".","_")
        
        #now constructiong the SQL query
        sql = """
             SELECT DISTINCT `chromosome`,     
                    `position`, 
                    `SNP_name`,
                    `Alleles_A_B_FORWARD`,
                    `Alleles_A_B_Affymetrix`
               FROM `{table}`
              WHERE `chromosome` = %s AND
                    `position` = %s AND
                    `SNP_name` = %s
        """.format(table=table)
        
        #Query the database
        conn = self.getConnection()
        curs = conn.cursor()
        
        #debug
        logger.debug("Querying '%s' using '%s'" %(table, conn))

        #Now process each line of VEP input
        header = None
        data = []
        
        #Cicling along vep_input_data
        for vep_input in vep_input_data:
            logger.debug("search for %s" %(vep_input.__str__()))
            n_of_rows = curs.execute(sql, vep_input)
            
            if n_of_rows == 0:
                raise snpchimpDBException, "%s return %s records" %(sql.replace("%s","'%s'") %vep_input, n_of_rows)
                
            if header == None:
                header = [col[0] for col in curs.description]
            
            #retrieve results and convert them in lists
            results = curs.fetchall()
            results = [list(result) for result in results]
            
            #Add this results to global results
            data += list(results)

        #debug
        logger.info("Got %s variants from %s" %(len(data), table))

        #Adding header        
        data.insert(0, header)
        
        #returning results
        return data
        
    
#The supported assemblies (snpchimp assembly name 2 ensembl assembly name - default_coord_system_version)
#the key values read by ConfigParser in module Utils.snpchimpDB are always in lower case
SUPPORTED_ASSEMBLIES = {
    'galgal40': u'Galgal4',
    'umd3': u'UMD3.1',
    'equcab2_0': u'EquCab2',
    'sscrofa_10_2': u'Sscrofa10.2',
    'oar_3_1': u'Oar_v3.1'
}

