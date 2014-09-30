# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 12:18:43 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A series of useful function

"""

def parseVePinput(snpchimp_data):
    """Parse vep_input_string from snpchimp downloadSNP.php scripts call"""
    
    parsed_data = []
    
    for line in snpchimp_data.split(","):
        tmp = line.split(":")
        parsed_data += [tuple(tmp)]
        
    return parsed_data
    
def getUniqueList(a_list):
    """Return al list with unique values"""
    
    return list(set(a_list))
    
