# -*- coding: utf-8 -*-
"""

Created on Tue Jul 15 16:48:15 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.it>

"""

ENSEMBL_REST_SERVER = 'http://rest.ensembl.org/'

ENSEMBL_REST_VERSION = u'3.1.0'

ENSEMBL_MIME_TYPES = {
    'fasta' : {
        'content_type' : 'text/x-fasta',
        'extension' : '.fasta',
        'notes' : """Sequence serialisation format. Only supported on the /sequence endpoint"""
    },

    'gff3' : {
        'content_type' : 'text/x-gff3',
        'extension' : '.gff3',
        'notes' : """Genomic feature serialisation format. Only supported on the /feature endpoint."""
    },

    #TODO: Add other mime types (https://github.com/Ensembl/ensembl-rest/wiki/Output-formats)

    'json' : {
        'content_type' : 'application/json',
        'extension' : '.json',
        'notes' : """JavaScript compatible generic text based serialisation format. Supported by most programming languages and the recommended consumption format"""
    },

    'jsonp' : {
        'content_type' : 'text/javascript',
        'extension' : '.jsonp',
        'notes' : """Extension of JSON to avoid issues of web browser same origin policy. Commonly used by JavaScript plugins like jQuery."""
    },

    'text' : {
        'content_type' : 'text',
        'extension' : '.html',
        'notes' : "No description in Ensembl REST documentation (https://github.com/Ensembl/ensembl-rest/wiki/Output-formats)"
    },

    'xml' : {
        'content_type' : 'text/xml',
        'extension' : '.xml',
        'notes' : '',
    },

    'yaml' : {
        'content_type' : 'text/x-yaml',
        'extension' : '.yaml',
        'notes' : '',
    },
}

ENSEMBL_ENDPOINTS = {
    #Information Endpoints
    'getAssembliesBySpecie' : {
        'description' : "List the currently available assemblies for a species",
        'url' : "info/assembly/:species",
        'method' : "GET",
        'response_formats' : ["json", "xml", "jsonp"],
        'default_content_type' : ENSEMBL_MIME_TYPES['json']['content_type'],
        'required_params' : ["species"],
        'optional_params' : ["bands", "callback"],
    },

    'getAllAvailableSpecies' : {
        'description' : "Lists all available species, their aliases, available adaptor groups and data release.",
        'url' : "info/species",
        'method' : "GET",
        'response_formats' : ["json", "xml", "jsonp"],
        'default_content_type' : ENSEMBL_MIME_TYPES['json']['content_type'],
        'required_params' : [],
        'optional_params' : [],
    },

    #Sequences EndPoints
    'getSequenceByID' : {
        'description' : "Request multiple types of sequence by stable identifier.",
        'url' : "sequence/id/:id",
        'method' : "GET",
        'response_formats' : ["fasta", "json", "jsonp", "text", "yaml"],
        'default_content_type' : ENSEMBL_MIME_TYPES['fasta']['content_type'],
        'required_params' : ['id'],
        'optional_params' : ['db_type', 'expand_3prime', 'expand_5prime', 'format', 'mask', 'mask_feature', 'multiple_sequences', 'object_type', 'species', 'type'],
    },

    'getSequenceByRegion' : {
        'description' : "Returns the genomic sequence of the specified region of the given species.",
        'url' : "sequence/region/:species/:region",
        'method' : "GET",
        'response_formats' : ["fasta", "json", "jsonp", "text", "yaml"],
        'default_content_type' : ENSEMBL_MIME_TYPES['fasta']['content_type'],
        'required_params' : ['region', 'species'],
        'optional_params' : ['coord_system', 'coord_system_version', 'expand_3prime', 'expand_5prime', 'format', 'mask', 'mask_feature'],
    },

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
        'description' : 'Fetch variant consequences (for a single region)',
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

#Logging istance
#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
