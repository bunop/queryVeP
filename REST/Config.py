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

    'xml' : {
        'content_type' : 'text/xml',
        'extension' : '.xml',
        'notes' : '',
    },
}

ENSEMBL_ENDPOINTS = {
    #Variation endpoints
    'getVariationsFeaturesById': {
        'description' : "Uses a variation identifier (e.g. rsID) to return the variation features",
        'url': 'variation/:species/:id',
        'method': 'GET',
        'response_formats' : ['json', 'xml', 'jsonp'],
        'default_content_type' : ENSEMBL_MIME_TYPES['json']['content_type'],
        'required_params' : ['id', 'species'],
        'optional_params' : ['callback', 'genotypes', 'phenotypes', 'pops'],
    },

    'getVariantConsequencesById': {
        'description' : 'Fetch variant consequences based on a variation identifier',
        'url': 'vep/:species/id/:id',
        'method': 'GET',
        'response_formats' : ['json', 'xml', 'jsonp'],
        'default_content_type' : ENSEMBL_MIME_TYPES['json']['content_type'],
        'required_params' : ['id', 'species'],
        'optional_params' : ['callback', 'canonical', 'ccds', 'domains', 'hgvs', 'numbers', 'protein', 'xref_refseq'],
    },

    'getVariantConsequencesByMultipleIds' : {
        'description' : 'Fetch variant consequences for multiple ids',
        'url': 'vep/:species/id/',
        'method': 'POST',
        'response_formats' : ['json', 'xml', 'jsonp'],
        'default_content_type' : ENSEMBL_MIME_TYPES['json']['content_type'],
        'required_params' : ['species'],
        'optional_params' : ['callback', 'canonical', 'ccds', 'domains', 'hgvs', 'numbers', 'protein', 'xref_refseq'],
        'message_param' : 'ids',
    },

    'getVariantConsequences' : {
        'description' : 'Fetch variant consequences',
        'url' : 'vep/:species/region/:region/:allele/',
        'method' : 'GET',
        'response_formats' : ['json', 'xml', 'jsonp'],
        'default_content_type' : ENSEMBL_MIME_TYPES['json']['content_type'],
        'required_params' : ['allele', 'region', 'species'],
        'optional_params' : ['callback', 'canonical', 'ccds', 'domains', 'hgvs', 'numbers', 'protein', 'xref_refseq'],
    },

    'getVariantConsequencesByMultipleRegions' : {
        'description' : 'Fetch variant consequences for multiple regions',
        'url' : 'vep/:species/region/',
        'method' : 'POST',
        'response_formats' : ['json', 'xml', 'jsonp'],
        'default_content_type' : ENSEMBL_MIME_TYPES['json']['content_type'],
        'required_params' : ['species'],
        'optional_params' : ['callback', 'canonical', 'ccds', 'domains', 'hgvs', 'numbers', 'protein', 'xref_refseq'],
        'message_param' : 'variants',
    },

    #TODO: Add other ensembl EndPoints

}

ENSEMBL_SUPPORTED_CODES = {
    200: {
        'name' : 'OK',
        'notes' : 'Request was a success. Only process data from the service when you receive this code',
    },

    400: {
        'name' : 'Bad Request',
        'notes' : 'Occurs during exceptional circumstances such as the service is unable to find an ID. Check if the response Content-type or Accept was JSON. If so the JSON object is an exception hash with the message keyed under error',
    },

    403 : {
        'name' : 'Forbidden',
        'notes' : 'You are submitting far too many requests and have been temporarily forbidden access to the service. Wait and retry with a maximum of 15 requests per second.',
    },

    404 : {
        'name' : 'Not Found',
        'notes' : 'Indicates a badly formatted request. Check your URL',
    },

    408 : {
        'name' : 'Timeout',
        'notes' : 'The request was not processed in time. Wait and retry later',
    },

    429 : {
        'name' : 'Too Many Requests',
        'notes' : 'You have been rate-limited; wait and retry. The headers  X-RateLimit-Reset ,  X-RateLimit-Limit  and  X-RateLimit-Remaining  will inform you of how long you have until your limit is reset and what that limit was. If you get this response and have not exceeded your limit then check if you have made too many requests per second.',
    },

    503 : {
        'name' : 'Service Unavailable',
        'notes' : 'The service is temporarily down; retry after a pause',
    },

}