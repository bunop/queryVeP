# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 16:36:59 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A program to open a CSV (or TSV) SNPchimp downloaded file and query ensembl via REST.
Now I wouldn't search by creating a VCF file. I will use the default ensembl imput file,
ex:

1   881907    881906    -/C   +
5   140532    140532    T/C   +
12  1017956   1017956   T/A   +
2   946507    946507    G/C   +
14  19584687  19584687  C/T   -
19  66520     66520     G/A   +    var1
8   150029    150029    A/T   +    var2

chromosome - just the name or number, with no 'chr' prefix
start
end
allele - pair of alleles separated by a '/', with the reference allele first
strand - defined as + (forward) or - (reverse).
identifier - this identifier will be used in the VEP's output. If not provided, the VEP will construct an identifier from the given coordinates and alleles.

"""

import csv
import sys
import logging
import REST.EndPoints
import EnsEMBL.VEP

#Logging istance for main application
#logger = logging.getLogger()
#logger.setLevel(logging.INFO)
#
##Setting loggin level for imported modules
##logging.getLogger(name="REST.EndPoints").setLevel(logging.WARN)
#
## default handler is sys.stderr
#handler = logging.StreamHandler()
#handler.setLevel(logging.DEBUG)
#
## Setting the format of logging and assign it to handler
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)
#
## add the handlers to the logger
#logger.addHandler(handler)

#Logging istance
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()

#My EnsEMBL REST ISTANCE
EnsREST = REST.EndPoints.EnsEMBLEndPoint()

#My local REST instance
#EnsREST = REST.EndPoints.EnsEMBLEndPoint(server="http://localhost:3000")

#testing if server is active
#if not EnsREST.ping():
#    raise Exception, "Server %s seems to be down" %(EnsREST.server)

filename = "SNPchimp_result_1454816959.csv"

#determine infile format
handle = open(filename)
header = handle.next()
Sniffer = csv.Sniffer()
dialect = Sniffer.sniff(header)

#restart to read the file
handle.seek(0)

#Open csv file
csvin = csv.reader(handle, dialect=dialect)

#This is the header of the file
header = csvin.next()

#TODO: Some line in input file differ only for SNP origin. Try to deal with this

#Now I need to convert data like defaul VEP input file
chr_idx = header.index("chromosome")
pos_idx = header.index("position")
id_idx = header.index("SNP_name")

#This is the NCBI allele definition of the SNPs. Maybe it isn't equal to allele of Illumina of Affymetrix
#alleles_idx = header.index("alleles")
illu_idx = header.index("Alleles_A_B_FORWARD")
affy_idx = header.index("Alleles_A_B_Affymetrix")

#The orientation column is the strand column in ensembl
strand_idx = header.index("orient")

#A function to interpret strand correctly
def getStrand(strand):
    if strand == "reverse":
        return "-"
    else:
        return "+"

#the last 3 columns will be "."
#qual_idx
#filter_idx
#info_idx

#defining snpchimp data like dictionary (in order to call API rest)
snpchimp = {'variants' : []}

#Now I will write each line of the input data in a file
outfilename = "VEP_SNPchimp_result_1454816959.tsv"
outhandle = open(outfilename, "w")
csvout = csv.writer(outhandle, delimiter="\t", lineterminator="\n")

#There are some record that are duplicated. They are the same SNPs derived from
#differente chips
uniq_dict = {}
counter = 0

#Now iterating across snpchimp data
for line in csvin:
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
        raise Exception, "affy_allele (%s) and illu_allel (%s) are BOTH defined"

    #The strand codified as ensembl
    strand = getStrand(line[strand_idx])

    row = [chrom, pos, pos, allele, strand, ID]
    key = tuple(row)

    #if I have already defined this row, I take note but I will continue to another row
    if uniq_dict.has_key(key):
        uniq_dict[key] += 1
        continue

    else:
        uniq_dict[key] = 1

    #default_line = [chrom, pos, pos, alleles, strand, ID]
    default_line = "\t".join([str(el) for el in row])

    logger.debug("default_line: %s" %(default_line))

    #Write this line in output file
    csvout.writerow(row)

    snpchimp["variants"] += [default_line]

    counter += 1

    #debug
    if counter >= 25:
        break

#closing inputfile and output file
handle.close()
outhandle.close()

logger.info("readed %s SNP lines" %(counter))

logger.info("Perform REST request")
#results ordering is determined by REST system
results = EnsREST.getVariantConsequencesByMultipleRegions(species="cow", variants=snpchimp, canonical=1, ccds=1, domains=1, hgvs=1, numbers=1, protein=1, xref_refseq=1)
logger.info("REST replies with %s results" %len(results))

#Ordering results as input data
results = sorted(results, key=lambda result:snpchimp["variants"].index(result["input"]))

#my results
variants = []

#Now cicle through each result and print a tuple. Write similar as VEP output
for result in results:
    variant = EnsEMBL.VEP.Variant(result)
    logger.debug(variant)
    variants += [variant]

#Now write results in a convenient way
csvout = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")

#defined the results header format
header = ['#Uploaded_variation', 'Location', 'Allele', 'Gene', 'Feature', 'Feature_type', 'Consequence', 'cDNA_position', 'CDS_position', 'Protein_position', 'Amino_acids', 'Codons', 'Existing_variation', 'Extra']
csvout.writerow(header)

for var in variants:
    for record in var.getVEPRecord():
        csvout.writerow(record)

