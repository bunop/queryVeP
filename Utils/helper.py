# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 12:18:43 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A series of useful function

"""

import re
import csv
import logging
import HTMLTags

# Logger instance
logger = logging.getLogger(__name__)

# import snpchimpDBException from snpchimpDB module
from snpchimpDB import snpchimpDBException

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
    
def iter_snpChimp_variants(header, snpChimp_variants):
    """An internal function to deal with common feature derived from snpchimp variant"""
    
    #Now I need to convert data like default VEP input file
    chr_idx = header.index("chromosome")
    pos_idx = header.index("position")
    id_idx = header.index("SNP_name")

    #This is the NCBI allele definition of the SNPs. Maybe it isn't equal to allele of Illumina of Affymetrix
    #alleles_idx = header.index("alleles")
    illu_idx = header.index("Alleles_A_B_FORWARD")
    affy_idx = header.index("Alleles_A_B_Affymetrix")

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
        #a missing allele could be 0/0 or NULL, 0/0 uf there are affymatrix or illumina data
        #NULL if specie lack completely of affimetrix or illumina data. Columns are
        #always the same so table are identical
        if (affy_allele == 'NULL' or affy_allele == '0/0') ^ (illu_allele == 'NULL' or illu_allele == '0/0'):
            if (affy_allele != '0/0' and affy_allele != 'NULL'):
                allele = affy_allele

            else:
                allele = illu_allele

        else:
            raise snpchimpDBException, "affy_allele (%s) and illu_allele (%s) are BOTH defined for %s" %(affy_allele, illu_allele, line)

        #check for insert and deletions in alleles (a generic case)
        if "I" in allele.upper() or "D" in allele.upper():
            raise snpchimpDBException, "Cannot handle Inserts or Deletions in alleles!!!"
            
        #TODO: shall I avoid this particoular case?

        #the strand is always positive
        strand = "+"
        
        #returning parsed data as a LIST
        yield [count, chrom, pos, ID, allele, strand]
    
def SNPchiMp2VCF(header, snpChimp_variants, out_handle):
    """get header, snpchimp variants and write a VCF in a open file handle"""
    
    #define the VCF as a TSV file
    csvout = csv.writer(out_handle, delimiter="\t", lineterminator="\n")
    
    for [count, chrom, pos, ID, allele, strand] in iter_snpChimp_variants(header, snpChimp_variants):
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

    logger.info("%s line(s) processed" %(count+1))

def SNPchiMp2VEPinput(header, snpChimp_variants, out_handle):
    """get header, snpchimp variants and write a standard VEP input file in a open 
    file handle"""

    #define the default VEP input file as a TSV file
    csvout = csv.writer(out_handle, delimiter="\t", lineterminator="\n")

    #Now iterating across snpchimp data
    for [count, chrom, pos, ID, allele, strand] in iter_snpChimp_variants(header, snpChimp_variants):
        #the first allele in VEP input is the reference allele. I cannot know what 
        #the reference allele is from snpchimp data. I define the ref allele as a N
        allele = "/".join(["N", allele])
        
        #this row is in ensembl default VEP input format
        row = [chrom, pos, pos, allele, strand, ID]
        
        #TODO: determine the REF base of the SNP

        #vep input line
        vep_line = "\t".join([str(el) for el in row])

        #counted lines start from 0
        logger.debug("VEP input line %s: '%s'" %(count+1, vep_line))

        #Write this line in output file
        csvout.writerow(row)
        
    
#Instantiate a generic class from a dict
class DummyClass(object):
    """Instantiate a class object from a dictionary. All keys become class attributes"""
    
    def __init__(self, *initial_data, **kwargs):
        """Instantiate the class like DummyClass({"name": "abc", "age": 32}) or 
        DummyClass({"name": "abc", "age": 32}) or both"""
        
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
                
        for key in kwargs:
            setattr(self, key, kwargs[key])

#A function to parse location and to return chrom, start and end in a list
def parseLocation(location):
    #A function to parse location and to return chrom, start and end in a list
    pattern = re.compile("^([^:]+):([0-9]+)\.\.([0-9]+)$")
    match = re.search(pattern, location)
    
    if match == None:
        raise Exception, "Location must be expressed like <chrom>:<start>..<end>"
        
    chrom, start, end = match.groups()
    
    #Casting position as integer
    start = int(start)
    end = int(end)

    return chrom, start, end
    
#A function strictly similar to the linkify function of variant_effect_predictor.pl
def linkify(specie, field, allele=None):
    """A function able to make link from ensembl names"""
    
    #ensembl genes
    pattern = "(ENS.{0,3}G\d+|CCDS\d+\.?\d+?|N[MP]_\d+\.?\d+?)"
    (field, number) = re.subn(pattern, lambda match: str(HTMLTags.A("%s" %(match.groups()[0]), href="http://www.ensembl.org/%s/Gene/Summary?g=%s" %(specie, match.groups()[0]), target="_blank")),  field)
        
    #ensembl transcripts
    pattern = "(ENS.{0,3}T\d+)"    
    (field, number) = re.subn(pattern, lambda match: str(HTMLTags.A("%s" %(match.groups()[0]), href="http://www.ensembl.org/%s/Transcript/Summary?t=%s" %(specie, match.groups()[0]), target="_blank")),  field)

    # Ensembl regfeats
    pattern = "(ENS.{0,3}R\d+)"
    (field, number) = re.subn(pattern, lambda match: str(HTMLTags.A("%s" %(match.groups()[0]), href="http://www.ensembl.org/%s/Regulation/Summary?rf=%s" %(specie, match.groups()[0]), target="_blank")),  field)

    # variant identifiers
    pattern = "(rs\d+|COSM\d+|C[DMIX]\d+)"
    (field, number) = re.subn(pattern, lambda match: str(HTMLTags.A("%s" %(match.groups()[0]), href="http://www.ensembl.org/%s/Variation/Summary?v=%s" %(specie, match.groups()[0]), target="_blank")),  field)
    
    #split strings a put a space after ; and ,
    pattern = "([,;])"
    (field, number) = re.subn(pattern, lambda match: "%s " %match.groups()[0], field)
    
    #locations
    for match in re.finditer("(^[A-Z\_\d]+?:\d+)(\-\d+)?", field):
        #redefine location
        loc = match.groups()[0]
        if match.groups()[1] != None:
            loc += match.groups()[1]
        
        #splitting coordinates
        tmp = re.split("\-|\:", loc)
        
        #case chrom:start
        if len(tmp) == 2:
            chrom, start, end = tmp[0], int(tmp[1]), int(tmp[1])
        
        elif len(tmp) == 3:
            chrom, start, end = tmp[0], int(tmp[1]), int(tmp[2])
            
        else:
            raise Exception, "Unknown location %s" %(loc)
        
        #  adjust start and end with the same values used in VeP
        view_start = start - 10
        view_end = end + 10
        
        if allele == None:
            allele = "N"
        
        #make URL
        url = "http://www.ensembl.org/{specie}/Location/View?r={chrom}:{view_start}-{view_end};format=vep_input;custom_feature={chrom}%20{start}%20{end}%20{allele}%201;custom_feature=normal".format(chrom=chrom, view_start=view_start, view_end=view_end, start=start, end=end, allele=allele, specie=specie)
        
        #replacing position with link
        link = HTMLTags.A(loc, href=url, target="_blank")
        field = field.replace(loc, str(link), 1)

    return field
    
    
#  
#  # locations
#  while($string =~ m/(^[A-Z\_\d]+?:[1-9]\d+)(\-\d+)?/g) {
#    my $loc = $1.($2 ? $2 : '');
#    my ($chr, $start, $end) = split /\-|\:/, $loc;
#    $end ||= $start;
#    
#    # adjust +/- 1kb
#    my $view_start = $start - 10;
#    my $view_end   = $end + 10;
#    my $allele = $line->{Allele} || 'N';
#    
#    my $url =
#      "http://www.ensembl.org/$species/Location/View?".
#      "r=$chr:$view_start\-$view_end;format=vep_input;".
#      "custom_feature=$chr%20$start%20$end%20$allele%201;".
#      "custom_feature=normal";
#    
#    my $link = a({href => $url, target => "_blank"}, $string);
#    $string =~ s/$loc/$link/;
#  }
#  
#  #debug
#  print "$config, $field, $string, $line\n";
#  
#  return $string;
#}