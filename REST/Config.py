# -*- coding: utf-8 -*-
"""

Created on Tue Jul 15 16:48:15 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.it>

"""

ENSEMBL_REST_SERVER = 'http://rest.ensembl.org/'

ENSEMBL_MIME_TYPES = {
    'fasta' : {
        'content_type' : 'text/x-fasta',
        'extension' : '.fasta',
        'notes' : """Sequence serialisation format. Only supported on the /sequence endpoint"""
    },
    
    #TODO: Add other mime types (https://github.com/Ensembl/ensembl-rest/wiki/Output-formats)
    
    'json' : {
        'content_type' : 'application/json',
        'extension' : '.json',
        'notes' : """JavaScript compatible generic text based serialisation format. Supported by most programming languages and the recommended consumption format"""
    },
}

ENSEMBL_ENDPOINTS = {
    'Variation' : {
        #Variation endpoints
        'getVariationsFeaturesById': {
    		'url': 'variation/:species/:id',
    		'method': 'GET',
    		'content_type': 'application/json'
    	},
        
        'getVariantConsequencesById': {
            'url': 'vep/:species/id/:id',
            'method': 'GET',
            'response_formats' : ['json', 'xml', 'jsonp'], 
            'default_content_type' : ENSEMBL_MIME_TYPES['json']
        },
        
    },
    
    #TODO: Add other ensembl EndPoints
    
}

