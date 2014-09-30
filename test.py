#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 15:55:47 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Testing snpchimp downloadSNP.php script, to see which parameter are defined by POST method

"""

import cgi
import cgitb

from Utils.helper import parseVePinput

#Warning: These techniques expose information that can be used by an attacker. Use it only while developing/debugging. Once in production disable them.
cgitb.enable()

#debug
#cgi.test()

#reading calling parameters
form = cgi.FieldStorage()

animal = cgi.escape(form.getvalue("animal", None))
vep_input_string = cgi.escape(form.getvalue("vep_input_string", None))

print "Content-type: text/html"
print

print """
<html>

<head><title>testing downloadSNP.php</title></head>

<body>

  <h3> testing downloadSNP.php </h3>

  <p>animal: %s</p><br>
  <p>vep_input_string: %s</p><br>

</body>

</html>
""" %(animal, parseVePinput(vep_input_string))

