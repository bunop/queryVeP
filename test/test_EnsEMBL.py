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

#the module to test
import EnsEMBL.VEP

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
    
class test_QueryVEP(unittest.TestCase):
    vcf_str = "\n".join([getVCFline(snp1), getVCFline(snp2)])
    
    def setUp(self):
        """A test case to verify class assignment"""
        
        #the modulo to test
        self.QueryVEP = EnsEMBL.VEP.QueryVEP()
        
        #define VCF as a handle
        self.vcf_handle = StringIO.StringIO(vcf_str)