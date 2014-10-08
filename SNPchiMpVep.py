#! /var/www/cgi-bin/queryVeP/ENV/bin/python
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
from Utils.helper import parseSNPchiMpdata,getUniqueList,SNPchiMp2VCF
from Utils.snpchimpDB import SNPchiMp2

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
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger("SNPchiMpVep")

# mako template for CGI-HTML rendering
mylookup = mako.lookup.TemplateLookup(directories=["./mako_templates/"], module_directory='/tmp/%s-mako_modules' %(getpass.getuser()), output_encoding='utf-8', encoding_errors='replace', collection_size=500)
mytemplate = mylookup.get_template("index.html")

#reading calling parameters
form = cgi.FieldStorage()

#Those are needed parameters
animal = cgi.escape(form.getvalue("animal", None))
assembly = cgi.escape(form.getvalue("assembly", None))
vep_input_string = cgi.escape(form.getvalue("vep_input_string", None))
vep_input_data = getUniqueList(parseSNPchiMpdata(vep_input_string))

#debug
#print mytemplate.render(header=["animal", "assembly", "vep_input_data"], rows=[[animal, assembly, vep_input_data]])

#Try to fetch alleles in database
snpChimp = SNPchiMp2()
snpChimp.getConnection()
snpChimp_variants = snpChimp.getVariants(animal, assembly, vep_input_data)

#catch header
header = snpChimp_variants.pop(0)

#Debug: print the SNPchimp table in html output
#print mytemplate.render(header=header, rows=snpChimp_variants)

#Convert SNPchimp data into VCF.
vcf_handle = StringIO.StringIO()
SNPchiMp2VCF(header, snpChimp_variants, vcf_handle)

#Seeking vcf_handle to the start position
vcf_handle.seek(0)

#Use myclass data to do VEP requests
VEP = EnsEMBL.VEP.QueryVEP(inputfile=vcf_handle)

#debug set my internal REST server
VEP.setRESTserver("http://192.168.13.219:3000/")

#Query ensembl via REST
VEP.Query()

#defined the results header format
header = ['#Uploaded_variation', 'Location', 'Allele', 'Gene', 'Feature', 'Feature_type', 'Consequence', 'cDNA_position', 'CDS_position', 'Protein_position', 'Amino_acids', 'Codons', 'Existing_variation', 'Extra']

#those are results
rows = VEP.GetResults()

#TODO: check if assembly is correct in each variation

#print data with mako templayes
print mytemplate.render(header=header, rows=rows)

