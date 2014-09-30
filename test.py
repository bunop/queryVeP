#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 15:55:47 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Testing snpchimp downloadSNP.php script, to see which parameter are defined by POST method

"""

import cgi
import sys
import cgitb

from Utils.helper import parseVePinput,getUniqueList
from Utils.snpchimpDB import SNPchiMp2

#Adding virtualenv directory
sys.path.insert(0, "ENV/lib/python2.6/site-packages")

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

# mako template for CGI-HTML rendering
mylookup = mako.lookup.TemplateLookup(directories=["./mako_templates/"], module_directory='/tmp/mako_modules', output_encoding='utf-8', encoding_errors='replace', collection_size=500)
mytemplate = mylookup.get_template("index.html")

#reading calling parameters
form = cgi.FieldStorage()

#Those are needed parameters
animal = cgi.escape(form.getvalue("animal", None))
assembly = cgi.escape(form.getvalue("assembly", None))
vep_input_string = cgi.escape(form.getvalue("vep_input_string", None))
vep_input_data = getUniqueList(parseVePinput(vep_input_string))

print mytemplate.render(header=["animal", "assembly", "vep_input_data"], rows=[[animal, assembly, vep_input_data]])

#Try to fetch alleles in database
#snpChimp = SNPchiMp2()
#snpChimp.getConnection()
#results = snpChimp.getVariants(animal, assembly, vep_input_data)
#
##catch header
#header = results.pop(0)
#
#print mytemplate.render(header=header, rows=results)
#
