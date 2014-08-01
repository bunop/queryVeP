#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 31 12:25:06 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Uno script CGI in python per interrogare le api REST di ensembl e restituire una
tabella utilizzabile da snpChimp

TODO:
cerca l'allele di riferimento. Usa il VCF per fare le query. La coppia di SNP che
uso come input ne calcolo le consequenze.

"""

import os
import csv
import cgi
import cgitb
import logging
import tempfile
import EnsEMBL.VEP

#Per stampare le storie in CGI con i template mako
import mako
import mako.lookup
import mako.template

#TODO: These techniques expose information that can be used by an attacker. Use
#it only while developing/debugging. Once in production disable them.
cgitb.enable()

#Apetura dello stdout in modo che sia comprensibe dal browser
print("Content-type: text/html\n")

#TODO: Gestisci l'input leggendolo direttamente dal database

#Logging istance
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("queryREST-CGI")

#A function to interpret strand correctly
def getStrand(strand):
    if strand == "reverse":
        return "-"
    else:
        return "+"

#Lettura dei dati passati dal chiamante
form = cgi.FieldStorage()

# debug script with fake data
class dummy:
    def __init__(self, s):
        self.value = s

class dummy_file(dummy):
    def __init__(self, s):
        dummy.__init__(self,s)
        self.filename = self.value
        self.file = open(self.filename, "rU")

form = {'filename': dummy_file('test_snpchimp_out.csv'), 'specie':dummy('cow'), 'debug':dummy(1)}

# A nested FieldStorage instance holds the file
fileitem = form['filename']
specie = form['specie']
debug = bool(form['debug'].value)

# Recupero i mako templates
mylookup = mako.lookup.TemplateLookup(directories=["./mako_templates/"], module_directory='/tmp/mako_modules', output_encoding='utf-8', encoding_errors='replace', collection_size=500)
mytemplate = mylookup.get_template("index.html")

# Questo è il limite massimo di SNPs che posso fare con una sola richiesta
snps_limit = 25

# Test if the file was uploaded
if fileitem.filename:
    #per semplicità
    handle = fileitem.file
    Sniffer = csv.Sniffer()
    header = handle.next()
    dialect = Sniffer.sniff(header)

    #restart to read the file
    handle.seek(0)

    #Open csv file
    csvin = csv.reader(handle, dialect=dialect)

    #This is the header of the file
    header = csvin.next()

    #debug
    #print header

    #Now I need to convert data like defaul VEP input file
    chr_idx = header.index("chromosome")
    pos_idx = header.index("position")
    id_idx = header.index("SNP_name")

    #This is the NCBI allele definition of the SNPs. Maybe it isn't equal to allele of Illumina of Affymetrix
    #alleles_idx = header.index("alleles")
    illu_idx = header.index("Alleles_A_B_FORWARD")
    affy_idx = header.index("Alleles_A_B_Affymetrix")

    #The orientation column is the strand column in ensembl
    #TODO: lo strand è sempre +
    strand_idx = header.index("orient")

    #There are some record that are duplicated. They are the same SNPs derived from
    #differente chips
    uniq_dict = {}
    counter = 0

    #saving VEP input in a temporary file
    outfilename = tempfile.mkstemp(prefix="VEPinput_")[1]
    outhandle = open(outfilename, "w")
    csvout = csv.writer(outhandle, delimiter="\t", lineterminator="\n")

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
            raise Exception, "affy_allele (%s) and illu_allel (%s) are BOTH defined for %s" (affy_allele, illu_allele, line)

        #The strand codified as ensembl
        #TODO: lo strand è sempre +
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

        counter += 1

        #debug
        if counter >= snps_limit:
            logger.warn("requests are limited to %s SNPs" %(snps_limit))
            break

    #closing inputfile and output file
    handle.close()
    outhandle.close()

    logger.info("readed %s SNP lines" %(counter))

    #Use myclass data to do VEP requests
    VEP = EnsEMBL.VEP.QueryVEP()
    VEP.Open(outfilename)
    VEP.Query()

    #defined the results header format
    header = ['#Uploaded_variation', 'Location', 'Allele', 'Gene', 'Feature', 'Feature_type', 'Consequence', 'cDNA_position', 'CDS_position', 'Protein_position', 'Amino_acids', 'Codons', 'Existing_variation', 'Extra']

    #those are results
    rows = VEP.GetResults()

    #print data with mako templayes
    print mytemplate.render(header=header, rows=rows)

    #remove temporary filename
    os.remove(outfilename)


#debug
if debug == True:
    cgi.print_form(form)
    cgi.test()
