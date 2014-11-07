# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 12:04:47 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Testing Utils modules

"""

import sys
import StringIO
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
 
class test_helper(unittest.TestCase):
    #the default header
    header = ['chromosome', 'position', 'SNP_name', 'Alleles_A_B_FORWARD', 'Alleles_A_B_Affymetrix']
    
    #a series of test cases that MUST fail. Only the first object is real (at the moment)
    wrong_variants = [['4', 87546564L, 'oar3_OAR4_87546564', '0/0', 'NULL'], ['4', 87546564L, 'oar3_OAR4_87546564', 'NULL', '0/0' ], ['4', 87546564L, 'oar3_OAR4_87546564', 'NULL', 'NULL'], ['4', 87546564L, 'oar3_OAR4_87546564', '0/0', '0/0'], ['4', 87546564L, 'oar3_OAR4_87546564', '0/0', '0/0'], ['4', 87546564L, 'oar3_OAR4_87546564', 'I/D', 'NULL'], ['4', 87546564L, 'oar3_OAR4_87546564', 'D/I', 'NULL'], ['4', 87546564L, 'oar3_OAR4_87546564', 'IN/DE', 'NULL']]
    
    #TODO: Add the new type of variants (In/De) in test case. handle those cases
    
    #A series of correct variants
    correct_variants = [['1', 98367573L, 'BovineHD4100000577', 'A/G', '0/0'], ['1', 16947L, 'AX-18000040', '0/0', 'A/C'], ['1', 98367573L, 'BovineHD4100000577', 'A/G', 'NULL'], ['1', 16947L, 'AX-18000040', 'NULL', 'A/C']]
    
    #The wanted VCF line 'CHROM POS ID REF ALT QUAL FILTER INFO'
    vcf_lines = ["\t".join(['1', str(98367573L), 'BovineHD4100000577', 'N', 'A,G', '.', '.', '.\n']), "\t".join(['1', str(16947L), 'AX-18000040', 'N', 'A,C', '.', '.', '.\n'])] * 2
    
    #The wanted VEP input line 'chrom, pos, pos, allele, strand, ID'
    vep_lines = ["\t".join(['1', str(98367573L), str(98367573L), 'N/A/G', '+', 'BovineHD4100000577\n']), "\t".join(['1', str(16947L), str(16947L), 'N/A/C', '+', 'AX-18000040\n'])] * 2
        
    def setUp(self):
        """Testing helper module"""
        pass
        
        
    def test_WrongInput2VCF(self):
        """Testing if wrong variants raise Exception"""
        
        for wrong_variant in self.wrong_variants:
            #A StringIO testing handle
            test_handle = StringIO.StringIO()
            
            #the parameters in assertRaises are given to the function using kwargs
            self.assertRaises(Utils.helper.snpchimpDBException, Utils.helper.SNPchiMp2VCF, self.header, [wrong_variant], test_handle)
            
    def test_SNPchiMp2VCF(self):
        """Testing VCF from snpchimp data input"""
        
        for i, variant in enumerate(self.correct_variants):
            out_handle = StringIO.StringIO()
            Utils.helper.SNPchiMp2VCF(self.header, [variant], out_handle)
            out_handle.seek(0)
            self.assertEqual(out_handle.read(), self.vcf_lines[i])
            
    def test_SNPchiMp2VEPinput(self):
        """Testing VEP input file from snpchimp data input"""
        
        for i, variant in enumerate(self.correct_variants):
            out_handle = StringIO.StringIO()
            Utils.helper.SNPchiMp2VEPinput(self.header, [variant], out_handle)
            out_handle.seek(0)
            self.assertEqual(out_handle.read(), self.vep_lines[i])
   
#Doing tests
if __name__ == "__main__":
    #doing tests
    unittest.main()
    


