#! /opt/pyenv/versions/2.7.8/bin/python2.7
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 15:55:47 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Testing snpchimp downloadSNP.php script, to see which parameter are defined by POST method

"""

import cgi
import cgitb
import getpass
import logging
import StringIO

#My modules
import EnsEMBL.VEP
import EnsEMBL.Sequence
import EnsEMBL.Information

from Utils.helper import parseSNPchiMpdata,getUniqueList,SNPchiMp2VCF, linkifyTable
from Utils.snpchimpDB import SNPchiMp2, SUPPORTED_ASSEMBLIES

#Using mako templates to write html. Loading functions
import mako
import mako.lookup
import mako.template

#Warning: These techniques expose information that can be used by an attacker. Use it only while developing/debugging. Once in production disable them.
cgitb.enable()

#Apetura dello stdout in modo che sia comprensibe dal browser
print("Content-type: text/html\n")

#debug
#cgi.test()

#Logging istance
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("SNPchiMpVep")

logger.info("CGI script started")

# mako template for CGI-HTML rendering
mylookup = mako.lookup.TemplateLookup(directories=["./mako_templates/"], module_directory='/tmp/%s-mako_modules' %(getpass.getuser()), output_encoding='utf-8', encoding_errors='replace', collection_size=500)
mytemplate = mylookup.get_template("index.html")

#reading calling parameters
form = cgi.FieldStorage()

#debug
logger.debug("form: %s" %(form))

#Those are needed parameters
animal = cgi.escape(form.getvalue("animal", None))
assembly = cgi.escape(form.getvalue("assembly", None))
vep_input_string = cgi.escape(form.getvalue("vep_input_string", None))
vep_input_data = getUniqueList(parseSNPchiMpdata(vep_input_string))

#debug
#print mytemplate.render(header=["animal", "assembly", "vep_input_data"], rows=[[animal, assembly, vep_input_data]])
logger.debug("received animal: '%s'" %(animal))
logger.debug("received assembly: '%s'" %(assembly))
logger.debug("received vep_input_string: '%s'" %(vep_input_string))

#the key values read by ConfigParser in module Utils.snpchimpDB are always in lower case
assembly = assembly.lower()

#Try to fetch alleles in database
logger.info("Connecting with snpchimp database")
snpChimp = SNPchiMp2(configfile="snpchimp2_conf.ini")
snpChimp.getConnection()
snpChimp_variants = snpChimp.getVariants(animal, assembly, vep_input_data)

# debug
logger.debug("snpChimp_variants = %s" % (snpChimp_variants))

#catch header
header = snpChimp_variants.pop(0)

#debug
logger.info("Searching the reference alleles for snpChimp variants")

#find reference allele for snpChimp_variants
logger.debug("Searching for reference alleles...")
header, snpChimp_variants = EnsEMBL.Sequence.getReferenceVariants(header, snpChimp_variants, animal)

# debug
logger.debug("snpChimp_variants = %s" % (snpChimp_variants))

#Debug: print the SNPchimp table in html output
#print mytemplate.render(header=header, rows=snpChimp_variants)

#Convert SNPchimp data into VCF.
logger.debug("Convert SNPchimp data into VCF")
vcf_handle = StringIO.StringIO()
SNPchiMp2VCF(header, snpChimp_variants, vcf_handle)

#Seeking vcf_handle to the start position
vcf_handle.seek(0)

#Use myclass data to do VEP requests
VEP = EnsEMBL.VEP.QueryVEP(inputfile=vcf_handle, specie=animal)

#debug set my internal REST server
#VEP.setRESTserver("http://192.168.13.219:3000/")

#Query ensembl via REST
logger.info("Searching consequences using %s VEP endpoints" %(VEP.getRESTserver()))
VEP.Query()

#defined the results header format
header = ['#Uploaded_variation', 'Location', 'Allele', 'Gene', 'Feature', 'Feature_type', 'Consequence', 'cDNA_position', 'CDS_position', 'Protein_position', 'Amino_acids', 'Codons', 'Existing_variation', 'Extra']

#those are results
rows = VEP.GetResults()
logger.info("%s replies with %s results" %(VEP.getRESTserver(), len(rows)))

#check if assembly is correct in each variation. SUPPORTED_ASSEMBLIES[assembly]
#is a dictionary where keys are SNPchimp assembly, and values are HARD CODED ensembl assemblies
logger.debug("Checking assembly correctness...")
VEP.CheckAssembly(SUPPORTED_ASSEMBLIES[assembly])

#now transforming ensembl names in link
logger.debug("Add html link to table...")
rows = linkifyTable(rows, header, animal)
logger.debug("completed!")

#print data with mako templayes
print mytemplate.render(header=header, rows=rows)

#Scrip finish here
logger.info("CGI script finished")

