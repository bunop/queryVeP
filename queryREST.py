# -*- coding: utf-8 -*-
"""
Created on Fri Jul 18 17:19:07 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A program to open a CSV (or TSV) SNPchimp downloaded file and query ensembl via REST

"""

import csv
import logging
import REST.EndPoints

#Logging istance
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

#My EnsEMBL REST ISTANCE
EnsREST = REST.EndPoints.EnsEMBLEndPoint()

filename = "SNPchimp_result_2942742710.csv"

#determine infile format
handle = open(filename)
test = handle.next()
Sniffer = csv.Sniffer()
dialect = Sniffer.sniff(test)

#restart to read the file
handle.seek(0)

#Open csv file
csvin = csv.reader(handle, dialect=dialect)

#This is the header of the file
header = csvin.next()

#Now I need to convert data like VCF format (at least 8 column)
#like "21 26960070 rs116645811 G A . . ."
chr_idx = header.index("chromosome")
pos_idx = header.index("position")
id_idx = header.index("SNP_name")
#ref_idx = ?
alt_idx = header.index("alleles")

#the last 3 columns will be "."
#qual_idx
#filter_idx
#info_idx

#defining snpchimp data like dictionary (in order to call API rest)
snpchimp = {'variants' : []}

#Now iterating across snpchimp data
for i, line in enumerate(csvin):
    #debug
    if i >= 25:
        break

    #some intersting values
    chrom = line[chr_idx]
    pos = int(line[pos_idx])

    #in VCF, the alt column represent comma separated variant alleles (NOT REFEENCE!)
    vcf_str = " ".join([chrom, str(pos), line[id_idx], ".", line[alt_idx].replace("/", ","), ".", ".", "."])

    #debug
    logging.debug("vcf_str: %s" %(vcf_str))

    #Search for reference base in Ensembl
    logging.debug(EnsREST.getSequenceByRegion(species="cow", region="%s:%s..%s" %(chrom, pos-1, pos+1)))
    logging.debug("")

    snpchimp["variants"] += [vcf_str]




#This will be the ensembl endpoit
#logging.debug("Perform REST request")
#EnsREST = REST.EndPoints.EnsEMBLEndPoint()
#results = EnsREST.getVariantConsequencesByMultipleRegions(species="cow", variants=snpchimp)
#logging.debug("Finished")
