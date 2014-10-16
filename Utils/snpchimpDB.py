# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 10:17:27 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A series of function to deal with snpchim database

"""

import helper
import logging
import MySQLdb
import ConfigParser

# Logger instance
logger = logging.getLogger(__name__)

#The supported assemblies (snpchimp assembly name 2 ensembl assembly name - default_coord_system_version)
#the key values read by ConfigParser in module Utils.snpchimpDB are always in lower case
SUPPORTED_ASSEMBLIES = {
    'galgal40': u'Galgal4',
    'umd3': u'UMD3.1',
    'equcab2_0': u'EquCab2',
    'sscrofa_10_2': u'Sscrofa10.2',
    'oar_3_1': u'Oar_v3.1'
}

#the current supported animals in snpchimp VEP REST API
SUPPORTED_ANIMALS = ['chicken', 'cow', 'horse', 'pig', 'sheep']
UNSUPPORTED_ANIMALS = ['goat']

class configException(Exception): pass

class Config(ConfigParser.ConfigParser):
    """A class to deal with Config file"""
    def __init__(self, configfile):        
        #Read the global ini file with database credentials
        ConfigParser.ConfigParser.__init__(self)
        
        logger.debug("reading configfile %s" %(configfile))
        self.read(configfile)
        
    #some methods to get useful data from Config file
    def getAllowedAnimals(self):
        """Return a dictionary of allowed animals in a config file"""
        
        results = dict((k,v) for k,v in self.items("allowed_animals"))
        
        #removing unsupported animals
        for animal in UNSUPPORTED_ANIMALS:
            del(results[animal])
            
        return results
    
    def getAssembliesByAnimal(self, animal):
        """Return a dictionary of allowed assemblies giving an animal"""
            
        if animal not in self.getAllowedAnimals().keys():
            raise configException, "I couldn't find '%s_assemblies' in config file" %(animal)
            
        return dict((k,v) for k,v in self.items("%s_assemblies" %(animal)))
        
    def getSupportedAssemblyByAnimal(self, animal):
        """Return the EnsEMBL current supported assembly for this animal"""
        
        #get all the assemblies for such animal
        assemblies = self.getAssembliesByAnimal(animal)
        
        #now iterate among assemblies
        supported_assembly = None
        
        for assembly in assemblies.iterkeys():
            if assembly in SUPPORTED_ASSEMBLIES.keys():
                #add supported assembly for this animal if it is None
                if supported_assembly == None:
                    supported_assembly = assembly
                    
                else:
                    #in this case I've just seen a supported assebly
                    raise configException, "There are more supported assemblyes for %s (%s : %s)" %(animal, supported_assembly, assembly)
        
        #Return the supported assembly for this animal (this is the snpchimp supported assembly)
        if supported_assembly == None:
            raise configException, "%s hasn't a supported assembly" %(animal)
            
        return supported_assembly
        
    

class snpchimpDBException(Exception): pass

class SNPchiMp2():
    """A class top deal with snpchimp database"""
    
    def __init__(self,configfile):
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
    
    def getTableByAssembly(self, animal, assembly):
        """Check if animal and assembly are defined and returns table in SNPchimp
        database"""
        
        #check if animal is allowed
        if animal not in self.allowed_animals.keys():
            raise snpchimpDBException, "Animal %s isn't in %s database" %(animal, self.db)
            
        #Check assembly if exists
        assemblies = self.config.getAssembliesByAnimal(animal)
        
        if assembly not in assemblies.keys():
            raise snpchimpDBException, "Assembly '%s' isn't in '%s' database. Assemblies are %s" %(assembly, self.db, assemblies.keys())
            
        #derive the correct table
        prefix = self.allowed_animals[animal]
        
        #check if animal and assembly is allowed, and return table suffix
        suffix = assemblies[assembly]
        
        #Derive the correct table name
        table = "%s_join_%s" %(prefix, suffix)
        
        #no "." are in table. Correct table name
        table = table.replace(".","_")
        
        #returns table value
        return table
    
    def getVariants(self, animal, assembly, vep_input_data):
        """Query SNPchiMp2 database, using animal and assembly to identify the
        correct table. vep_input_data must derive from downloadSNP.php call from
        snpchimp, ad parsed by the parseVePinput of the helper script"""
        
        #TODO: check correctness of vep_input_data
        logger.info("%s variants received in input" %(len(vep_input_data)))
        
        table = self.getTableByAssembly(animal, assembly)
        
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
        
    def getVariantsByLocation(self, animal, assembly, location):
        """Query SNPchiMp2 database, using animal and assembly to identify the
        correct table. Location must be like this <chrom>:<start>..<end>"""
        
        #check locations
        logger.debug("Checking location %s" %location)
        
        try:
            chrom, start, end = helper.parseLocation(location)
        except Exception, message:
            raise snpchimpDBException, message
        
        logger.debug("Got chrom:%s, start:%s, end:%s" %(chrom, start, end))

        #Check table
        table = self.getTableByAssembly(animal, assembly)
        
        #now constructiong the SQL query. Is the same query done by snpchimp
        sql = """
             SELECT DISTINCT `chromosome`,     
                    `position`, 
                    `SNP_name`,
                    `Alleles_A_B_FORWARD`,
                    `Alleles_A_B_Affymetrix`
               FROM `{table}`
              WHERE `chromosome` = %s AND
                    `position` >= %s AND
                    `position` <= %s
        """.format(table=table)
        
        #Query the database
        conn = self.getConnection()
        curs = conn.cursor()
        
        #debug
        logger.debug("Querying '%s' using '%s'" %(table, conn))
        
        #Quering
        n_of_rows = curs.execute(sql, (chrom, start, end))
        header = [col[0] for col in curs.description]
        
        #debug
        logger.info("Got %s variants from %s" %(n_of_rows, table))        
        
        #retrieve results and convert them in lists
        results = curs.fetchall()
        results = [list(result) for result in results]
        
        #Adding header        
        results.insert(0, header)
        
        return results
        
    


