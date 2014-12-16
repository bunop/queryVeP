# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 14:15:59 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A library to deal with reference sequences

"""

import copy
import REST
import logging
import Bio.Seq
import Bio.SeqRecord


# Logger instance
logger = logging.getLogger(__name__)

def getReferenceVariants(header, snpChimp_variants, specie):
    """Retrieve reference sequence allele for snpChimp_variants"""

    #this is the POST size for a single request
    offset = 25
    
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
    
    #Add each location to an array
    regions = []
    idx = 0
    
    for i, variant in enumerate(snpChimp_variants):
        chrom, pos = variant[chr_idx], variant[pos_idx]
        location = "%s:%s..%s" %(chrom, pos, pos)
        
        logger.debug("Added location '%s' for variant '%s'" %(location, variant))
        
        #Add this location into a LIST
        regions += [location]
        
        #check the maximum number of locations
        if len(regions) >= offset:
            data = {'regions' : regions }
            logger.debug("Performing REQUEST with '%s'" %(data))
        
            #get reference allele
            results = EndPoint.getSequenceByMultipleRegions(species=specie, regions=data)
            logger.debug("REST replied with %s results" %(len(results)))
            
            #Add each reference allele to variant
            for result in results:
                ref_allele = result["seq"]
                snpChimp_variants[idx].append(ref_allele)
                idx += 1
                
            #reinitialize regions:
            regions = []
    
    #Outside cicle, do last request if necessary
    if len(regions) > 0:
        data = {'regions' : regions }
        logger.debug("Performing REQUEST with '%s'" %(data))
        results = EndPoint.getSequenceByMultipleRegions(species=specie, regions=data)
        logger.debug("REST replied with %s results" %(len(results)))          
        
        for result in results:
            ref_allele = result["seq"]
            snpChimp_variants[idx].append(ref_allele)
            idx += 1
            
    #check that each position was processed
    if idx != len(snpChimp_variants):
        raise Exception, "Not all reference variants where retrieved"
        
    #returning the new header and new variants alleles
    return header, snpChimp_variants
