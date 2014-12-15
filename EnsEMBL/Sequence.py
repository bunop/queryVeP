# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 14:15:59 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A library to deal with reference sequences

"""

import copy
import REST
import logging

# Logger instance
logger = logging.getLogger(__name__)

def getReferenceVariants(header, snpChimp_variants, specie):
    """Retrieve reference sequence allele for snpChimp_variants"""
    
    #define a new header and new snpChimp_variants
    header = copy.deepcopy(header)
    snpChimp_variants = copy.deepcopy(snpChimp_variants)
    
    #Now I need to convert data like default VEP input file
    chr_idx = header.index("chromosome")
    pos_idx = header.index("position")
    
    #Add a column to header
    header.append("ref_allele")
    
    #processing variants and get reference sequence
    EndPoint = REST.EndPoints.EnsEMBLEndPoint()
    
    for i, variant in enumerate(snpChimp_variants):
        chrom, pos = variant[chr_idx], variant[pos_idx]
        location = "%s:%s..%s" %(chrom, pos, pos)
        
        #get reference allele
        record = EndPoint.getSequenceByRegion(species=specie, region=location)
        ref_allele = record.seq.tostring() 
        
        variant.append(ref_allele)
        
    #returning the new header and new variants alleles
    return header, snpChimp_variants
    
