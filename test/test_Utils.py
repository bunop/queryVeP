# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 12:04:47 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Testing Utils modules

"""

import sys
import unittest

#Adding library modules path
sys.path.append("..")

import Utils.helper
import Utils.snpchimpDB

class test_Config(unittest.TestCase):
    #current supported animals
    animals = Utils.snpchimpDB.SUPPORTED_ANIMALS
    
    def setUp(self):
        """A test case to verify that I can read configfile"""
        
        self.Config = Utils.snpchimpDB.Config("../snpchimp2_conf.ini")
        
        
    def test_AllowedAnimals(self):
        """Testing allowed animals""" 
        
        animals = sorted(self.Config.getAllowedAnimals().keys())
        
        #For compatibility with python 2.3
        for animal in animals:
            self.assertTrue(animal in self.animals)
        
    def test_GoatAssemblyNotSupported(self):
        """Testing that goat assembly is not supported"""
        
        self.assertRaises(Utils.snpchimpDB.configException, self.Config.getSupportedAssemblyByAnimal, "goat")
        
    def test_SupportedAssemblies(self):
        """Testing current supported assemblies"""
        
        for animal in self.animals:
            self.Config.getSupportedAssemblyByAnimal(animal)
            
        
class test_SNPchiMp2(unittest.TestCase):
    def setUp(self):
        """Testing database connection and methods"""
        self.SNPchiMp2 = Utils.snpchimpDB.SNPchiMp2("../snpchimp2_conf.ini")
        
    def test_Connection(self):
        """Testing database connection"""
        
        conn = self.SNPchiMp2.getConnection()
        conn.stat()
        
    def test_VEPinput_table(self):
        """testing supported animal tables"""
        
        Config = self.SNPchiMp2.config
        conn = self.SNPchiMp2.getConnection()
        cursor = conn.cursor()
        
        for animal in Utils.snpchimpDB.SUPPORTED_ANIMALS:
            assembly = Config.getSupportedAssemblyByAnimal(animal)
            table = self.SNPchiMp2.getTableByAssembly(animal, assembly)
            cursor.execute("DESCRIBE `%s`" %(table))
            try:
                self.checkColumn(cursor.fetchall())
            except Exception, message:
                raise Exception, "table:%s %s" %(table, message)
            
    def checkColumn(self, description):
        """Check column from DESCRIBE table results"""
        
        #parse column from description
        columns = [col[0] for col in description]
        
        #Those are my mnandatory columns
        to_check = ['chromosome', 'position', 'SNP_name', 'Alleles_A_B_FORWARD', 'Alleles_A_B_Affymetrix']
        
        for column in to_check:
            if not column in columns:
                raise Exception, "Column %s not found" %(column)
    
#Doing tests
if __name__ == "__main__":
    #doing tests
    unittest.main()