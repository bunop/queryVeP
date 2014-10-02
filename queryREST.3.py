# -*- coding: utf-8 -*-
"""

Modified on Mon Jul 28 12:00:58 2014

Performing REST VEP on large input. Opening inputfile as handle

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

import os
import csv
import sys
import types
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

# A class to deal with input data
class QueryVEP():
    def __init__(self, inputfile=None):
        self._offset = 50
        self._handle = None
        self._input = []
        self._results = []
        self._variants = []
        self._rest = REST.EndPoints.EnsEMBLEndPoint()

        if inputfile != None:
            self.Open(inputfile)

    def Open(self, inputfile):
        """Open a file for REST requests"""

        #Handle case
        if type(inputfile) == types.FileType:
            self._handle = inputfile

        elif type(inputfile) == types.StringType:
            self._handle = open(inputfile, "rU")

        else:
            raise Exception, "Cannot handle %s (%)" %(inputfile, type(inputfile))

    def Query(self):
        """Performing query requests"""

        #resetting variables:
        self._input = []
        self._results = []

        #read inputfile until self._offset lines. Do a query request then redo another request
        #open inputfile as it is (don't check input file type)
        counter = 0
        tmp_input = []

        for line in self._handle:
            counter += 1
            tmp_input += [line]

            if counter % self._offset == 0:
                self._queryREST(tmp_input)

                #resetting tmp values
                tmp_input = []

        #Ensuring that all the requests were done
        if len(tmp_input) > 0:
            self._queryREST(tmp_input)

        #Now trasform results in ensembl classes
        self._variants = []

        #Now cicle through each result and print a tuple. Write similar as VEP output
        for result in self._results:
            variant = EnsEMBL.VEP.Variant(result)
            logger.debug(variant)
            self._variants += [variant]


    def _queryREST(self, tmp_input):
        #perform a REST request
        tmp_variants = {'variants': tmp_input}

        logger.debug("Perform REST request")
        tmp_results = self._rest.getVariantConsequencesByMultipleRegions(species="cow", variants=tmp_variants, canonical=1, ccds=1, domains=1, hgvs=1, numbers=1, protein=1, xref_refseq=1)
        logger.debug("REST replies with %s results" %len(tmp_results))

        #Sort result by input order
        tmp_results = sorted(tmp_results, key=lambda result:tmp_variants["variants"].index(result["input"]))

        #record inputs (debug)
        self._input += tmp_input
        self._results += tmp_results

    def GetResults(self):
        """Return a list of ENSEMBL VEP records"""

        records = []

        for var in self._variants:
            for record in var.getVEPRecord():
                records += [record]

        return records

    def GetVariantByID(self, ID):
        """Return a variants by ID"""

        for i, variant in enumerate(self._variants):
            if variant.id == ID:
                return self._results[i], variant

        return None

#A function to interpret strand correctly
def getStrand(strand):
    if strand == "reverse":
        return "-"
    else:
        return "+"

if __name__ == "__main__":
    #My input file
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

    #Now I will write each line of the input data in a file
    outfilename = "VEP_%s.tsv" %(os.path.splitext(filename)[0])
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

        counter += 1

        #debug
#        if counter >= 25:
#            break

    #closing inputfile and output file
    handle.close()
    outhandle.close()

    logger.info("readed %s SNP lines" %(counter))

    #Use myclass data to do VEP requests
    VEP = QueryVEP()
    VEP.Open(outfilename)
    VEP.Query()

    #Now write results in a convenient way
    csvout = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")

    #defined the results header format
    header = ['#Uploaded_variation', 'Location', 'Allele', 'Gene', 'Feature', 'Feature_type', 'Consequence', 'cDNA_position', 'CDS_position', 'Protein_position', 'Amino_acids', 'Codons', 'Existing_variation', 'Extra']
    csvout.writerow(header)

    for record in VEP.GetResults():
        csvout.writerow(record)

