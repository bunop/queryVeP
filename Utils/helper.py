# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 12:18:43 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A series of useful function

"""

import csv
import logging

# Logger instance
logger = logging.getLogger(__name__)

def parseSNPchiMpdata(snpchimp_data):
    """Parse SNPchiMp from snpchimp downloadSNP.php scripts call and generate tuples
    in order to query SNPchiMp database"""
    
    parsed_data = []
    
    for line in snpchimp_data.split(","):
        tmp = line.split(":")
        parsed_data += [tuple(tmp)]
        
    return parsed_data
    
def getUniqueList(a_list):
    """Return al list with unique values"""
    
    return list(set(a_list))
    
def SNPchiMp2VCF(header, snpChimp_variants, out_handle):
    """get header, snpchimp variants and write a VCF in a open file handle"""
    
    #Now I need to convert data like default VEP input file
    chr_idx = header.index("chromosome")
    pos_idx = header.index("position")
    id_idx = header.index("SNP_name")

    #This is the NCBI allele definition of the SNPs. Maybe it isn't equal to allele of Illumina of Affymetrix
    #alleles_idx = header.index("alleles")
    illu_idx = header.index("Alleles_A_B_FORWARD")
    affy_idx = header.index("Alleles_A_B_Affymetrix")

    #define the VCF as a TSV file
    csvout = csv.writer(out_handle, delimiter="\t", lineterminator="\n")

    #Now iterating across snpchimp data
    for count, line in enumerate(snpChimp_variants):
        #some intersting values
        chrom = line[chr_idx]
        pos = int(line[pos_idx])
        ID = line[id_idx]

        #The illumina of affy allele
        affy_allele = line[affy_idx]
        illu_allele = line[illu_idx]

        #One of affymetrix or illumina should be defined. XOR conditions
        if (affy_allele == '0/0') ^ (illu_allele == '0/0'):
            if (affy_allele != '0/0'):
                allele = affy_allele

            else:
                allele = illu_allele

        else:
            raise Exception, "affy_allele (%s) and illu_allel (%s) are BOTH defined for %s" (affy_allele, illu_allele, line)

        #the strand is always positive
        #strand = "+"

        #this row is in ensembl default VEP input format
        #row = [chrom, pos, pos, allele, strand, ID]

        #because allele in SNPchimp doesn't like as VEP input, I will threat them like
        #multiple VCF variant allele. IMPORTANT: in VCF variant alleles are separated by ","
        allele = allele.replace("/", ",")

        #VCF input string is 'CHROM POS ID REF ALT QUAL FILTER INFO'
        row = [chrom, pos, ID, "N", allele, ".", ".", "."]
        
        #TODO: determine the REF base of the SNP

        #VCF format 'CHROM POS ID REF ALT QUAL FILTER INFO'
        vcf_line = "\t".join([str(el) for el in row])

        #counted lines start from 0
        logger.debug("VCF line %s: '%s'" %(count+1, vcf_line))

        #Write this line in output file
        csvout.writerow(row)

    logger.info("%s line(s) processed" %(count))

def SNPchiMp2VEPinput(header, snpChimp_variants, out_handle):
    """get header, snpchimp variants and write a standard VEP input file in a open 
    file handle"""
    
    #Now I need to convert data like default VEP input file
    chr_idx = header.index("chromosome")
    pos_idx = header.index("position")
    id_idx = header.index("SNP_name")

    #This is the NCBI allele definition of the SNPs. Maybe it isn't equal to allele of Illumina of Affymetrix
    #alleles_idx = header.index("alleles")
    illu_idx = header.index("Alleles_A_B_FORWARD")
    affy_idx = header.index("Alleles_A_B_Affymetrix")

    #define the VCF as a TSV file
    csvout = csv.writer(out_handle, delimiter="\t", lineterminator="\n")

    #Now iterating across snpchimp data
    for count, line in enumerate(snpChimp_variants):
        #some intersting values
        chrom = line[chr_idx]
        pos = int(line[pos_idx])
        ID = line[id_idx]

        #The illumina of affy allele
        affy_allele = line[affy_idx]
        illu_allele = line[illu_idx]

        #One of affymetrix or illumina should be defined. XOR conditions
        if (affy_allele == '0/0') ^ (illu_allele == '0/0'):
            if (affy_allele != '0/0'):
                allele = affy_allele

            else:
                allele = illu_allele

        else:
            raise Exception, "affy_allele (%s) and illu_allel (%s) are BOTH defined for %s" (affy_allele, illu_allele, line)

        #the strand is always positive
        strand = "+"

        #this row is in ensembl default VEP input format
        row = [chrom, pos, pos, allele, strand, ID]
        
        #FIXME: the first allele in VEP input is the reference allele. I cannot
        #know what the reference allele is from snpchimp data
        
        #TODO: determine the REF base of the SNP

        #vep input line
        vep_line = "\t".join([str(el) for el in row])

        #counted lines start from 0
        logger.debug("VEP input line %s: '%s'" %(count+1, vep_line))

        #Write this line in output file
        csvout.writerow(row)
        
    



