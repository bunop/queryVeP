# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 14:35:16 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Testing ensembl modules

"""

import sys
import logging
import unittest
import StringIO

#Adding library modules path
sys.path.append("..")

#the modules to test
import EnsEMBL.VEP
import EnsEMBL.Sequence
import EnsEMBL.Information


#where to find useful variables
from Utils.snpchimpDB import SUPPORTED_ANIMALS, UNSUPPORTED_ANIMALS, SUPPORTED_ASSEMBLIES, Config

#Logging istance
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
logger = logging.getLogger(__name__)

#Define the SNPs used as the query

#"21 26960070 rs116645811 G A . . ."
snp1=dict(chrom=1,pos=26960070,id="rs116645811",ref="G",alt="A")

#"21 26965148 rs1135638 G A . . ."
snp2=dict(chrom=1,pos=26965148,id="rs1135638",ref="G",alt="A")

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
    
    results = {
        "chicken" : [[u'rs116645811', u'1:26960070', u'A', u'ENSGALG00000009454', u'ENSGALT00000015386', 'Transcript', u'upstream_gene_variant', None, None, None, None, None, None, u'distance=52;gene_symbol_source=EntrezGene;gene_symbol=ZNF277;biotype=protein_coding;strand=-1'], [u'rs116645811', u'1:26960070', u'A', u'ENSGALG00000009480', u'ENSGALT00000038867', 'Transcript', u'upstream_gene_variant', None, None, None, None, None, None, u'distance=308;hgnc_id=HGNC:19192;gene_symbol_source=HGNC;gene_symbol=DOCK4;biotype=protein_coding;strand=1'], [u'rs1135638', u'1:26965148', u'A', u'ENSGALG00000009480', u'ENSGALT00000038867', 'Transcript', u'intron_variant', None, None, None, None, None, None, u'distance=0;hgnc_id=HGNC:19192;gene_symbol_source=HGNC;gene_symbol=DOCK4;biotype=protein_coding;strand=1']],
        "cow" : [[u'rs116645811', u'1:26960070', u'A', None, None, None, u'intergenic_variant', None, None, None, None, None, None, None], [u'rs1135638', u'1:26965148', u'A', None, None, None, u'intergenic_variant', None, None, None, None, None, None, None]],
        "horse" : [[u'rs116645811', u'1:26960070', u'A', None, None, None, u'intergenic_variant', None, None, None, None, None, None, None], [u'rs1135638', u'1:26965148', u'A', None, None, None, u'intergenic_variant', None, None, None, None, None, None, None]],
        "pig" : [[u'rs116645811', u'1:26960070', u'A', None, None, None, u'intergenic_variant', None, None, None, None, None, None, None], [u'rs1135638', u'1:26965148', u'A', None, None, None, u'intergenic_variant', None, None, None, None, None, None, None]],
        "sheep" : [[u'rs116645811', u'1:26960070', u'A', u'ENSOARG00000005633', u'ENSOART00000006140', 'Transcript', u'missense_variant', 1220, 1220, 407, u'G/D', u'gGc/gAc', None, u'distance=0;sift_score=0;hgnc_id=HGNC:25820;gene_symbol_source=HGNC;gene_symbol=ZYG11B;biotype=protein_coding;strand=1;sift_prediction=deleterious'], [u'rs1135638', u'1:26965148', u'A', u'ENSOARG00000005633', u'ENSOART00000006140', 'Transcript', u'intron_variant', None, None, None, None, None, None, u'distance=0;hgnc_id=HGNC:25820;gene_symbol_source=HGNC;gene_symbol=ZYG11B;biotype=protein_coding;strand=1']],
    }    
    
    def setUp(self):
        """A test case to verify class assignment"""
        
        #define VCF as a handle
        self.vcf_handle = StringIO.StringIO(vcf_str)
        
        #the modulo to test
        self.QueryVEP = EnsEMBL.VEP.QueryVEP(inputfile=self.vcf_handle)
        
        #internal testing
        #self.QueryVEP.setRESTserver("http://localhost:3000")
        
    def test_QueryVepOnSpecies(self):
        """Testing VEP rest api on SnpChimp species"""
        
        for animal in SUPPORTED_ANIMALS:
            self.vcf_handle.seek(0)
            self.QueryVEP.Open(inputfile=self.vcf_handle)
            #print animal,
            self.QueryVEP.Query(specie=animal)
            results = self.QueryVEP.GetResults()
            #print results
            self.assertListEqual(results, self.results[animal])
            

class test_Sequence(unittest.TestCase):
    """A class to defined Sequence module for sequence endpoints"""
    
    def setUp(self):
        self.header = ['chromosome', 'position', 'SNP_name', 'Alleles_A_B_FORWARD', 'Alleles_A_B_Affymetrix']
        self.snpChimp_variants = [['1', 434180L, 'BTA-07251-no-rs', 'T/C', '0/0'], ['1', 135098L, 'Hapmap43437-BTA-101873', 'A/G', '0/0'], ['1', 522543L, 'BovineHD4100000004', 'T/C', '0/0'], ['1', 822710L, 'BovineHD4100000005', 'A/G', '0/0'], ['1', 506410L, 'BovineHD4100000002', 'T/C', '0/0'], ['1', 393248L, 'Hapmap34944-BES1_Contig627_1906', 'A/C', '0/0'], ['1', 517814L, 'BovineHD4100000003', 'T/C', '0/0'], ['1', 516404L, 'Hapmap53946-rs29015852', 'T/C', '0/0']]
        self.animal = 'cow'
        
        #the results
        self.ref_alleles = [u'A', u'A', u'A', u'C', u'A', u'C', u'C', u'G']
        
    def test_getReferenceVariants(self):
        """Testing VEP rest enpoints to get reference variants"""
        
        #this is a method, not a class
        header, snpChimp_variants = EnsEMBL.Sequence.getReferenceVariants(self.header, self.snpChimp_variants, self.animal)
        idx = header.index("ref_allele")
        
        #get the retrieved reference alleles
        ref_alleles = [snpChimp_variant[idx] for snpChimp_variant in snpChimp_variants]
        
        #testing results
        self.assertListEqual(ref_alleles, self.ref_alleles)
        
   
#Doing tests
if __name__ == "__main__":
    #doing tests
    unittest.main()
    
