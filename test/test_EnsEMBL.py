# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 14:35:16 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Testing ensembl modules

"""

import sys
import unittest
import StringIO

#Adding library modules path
sys.path.append("..")

#the modules to test
import EnsEMBL.Information
import EnsEMBL.VEP

#where to find useful variables
from Utils.snpchimpDB import SUPPORTED_ANIMALS, UNSUPPORTED_ANIMALS, SUPPORTED_ASSEMBLIES, Config

#Define the SNPs used as the query

#"21 26960070 rs116645811 G A . . ."
snp1=dict(chrom=21,pos=26960070,id="rs116645811",ref="G",alt="A")

#"21 26965148 rs1135638 G A . . ."
snp2=dict(chrom=21,pos=26965148,id="rs1135638",ref="G",alt="A")

#a function to obtain a VCF line
def getVCFline(snp):
    """Get a VCF file by givin a SNP dict as input"""

    return "\t".join([str(snp["chrom"]), str(snp["pos"]), snp["id"], snp["ref"], snp["alt"], ".", ".","."])

#define a VCF like a string
vcf_str = "\n".join([getVCFline(snp1), getVCFline(snp2)])

class test_Information(unittest.TestCase):
    config = Config()
    
    def test_UnSupportedAnimals(self):
        """Testing unsupported animals"""
        
        for animal in UNSUPPORTED_ANIMALS:
            self.assertRaises(EnsEMBL.Information.InfoException, EnsEMBL.Information.getSpecieByName, animal )
            
    def test_SupportedAnimals(self):
        """Testing supported animals"""
        
        for animal in SUPPORTED_ANIMALS:
            specie = EnsEMBL.Information.getSpecieByName(animal)
            assembly = EnsEMBL.Information.getAssemblyByName(specie.name)
            
            #testing Ensembl default assembly with snpdb default assembly
            tmp = self.config.getSupportedAssemblyByAnimal(animal)
            test_assembly = SUPPORTED_ASSEMBLIES[tmp]
            
            self.assertEqual(test_assembly, assembly.default_coord_system_version)
    
class test_QueryVEP(unittest.TestCase):
    vcf_str = "\n".join([getVCFline(snp1), getVCFline(snp2)])
    
    def setUp(self):
        """A test case to verify class assignment"""
        
        #define VCF as a handle
        self.vcf_handle = StringIO.StringIO(vcf_str)
        
        #the modulo to test
        self.QueryVEP = EnsEMBL.VEP.QueryVEP(inputfile=self.vcf_handle)
        
    def test_QueryVepOnSpecies(self):
        """Testing VEP rest api on SnpChimp species"""
        
        for animal in SUPPORTED_ANIMALS:
            self.vcf_handle.seek(0)
            VeP = EnsEMBL.VEP.QueryVEP(inputfile=self.vcf_handle, specie=animal)
            VeP.Query()
#            results = VeP.GetResults()
#            print results
        
#Doing tests
if __name__ == "__main__":
    #doing tests
    unittest.main()
    
