# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 16:13:59 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A module to interact with VEP EnsEMBL REST results

"""

import REST
import types
import logging

# Logger instance
logger = logging.getLogger(__name__)

# an exception class for variant
class VariantException(Exception) : pass

# the default exception class of vep methods
class VePException(Exception) : pass

class ColocatedVariant():
    """A class to deal with variant and colocated variant"""

    def __init__(self, variant_dict=None):
        self.allele_string = None
        self.start = 0
        self.end = 0
        self.strand = None
        self.id = None

        if variant_dict != None:
            for key, value in variant_dict.iteritems():
                setattr(self, key, value)

    def __reprstr(self):
        return "id:%s; start:%s; end:%s; allele_string:%s" %(self.id, self.start, self.end, self.allele_string)

    def __repr__(self):
        return "%s.ColocatedVariant instance at %s (%s)" %(self.__module__, hex(id(self)), self.__reprstr())

    def __str__(self):
        return "%s.ColocatedVariant(%s)" %(self.__module__, self.__reprstr())

class TranscriptConsequence():
    "A class to deal with transcript consequences"

    def __init__(self, transcript_dict=None):
        self.biotype = None
        self.consequence_terms = []
        self.distance = 0
        self.gene_id = None
        self.gene_symbol = None
        self.gene_symbol_source = None
        self.strand = None
        self.transcript_id = None
        self.variant_allele = None
        self.cdna_start = None
        self.cdna_end = None
        self.cds_start = None
        self.cds_end = None
        self.protein_start = None
        self.protein_end = None
        self.amino_acids = None
        self.codons = None

        if transcript_dict != None:
            for key, value in transcript_dict.iteritems():
                setattr(self, key, value)

    def __reprstr(self):
        return "gene_id:%s; gene_symbol:%s; biotype:%s; strand:%s; distance:%s" %(self.gene_id, self.gene_symbol, self.biotype, self.strand, self.distance)

    def __repr__(self):
        return "%s.TranscriptConsequence instance at %s (%s)" %(self.__module__, hex(id(self)), self.__reprstr())

    def __str__(self):
        return "%s.TranscriptConsequence(%s)" %(self.__module__, self.__reprstr())

    def getExtraFeatures(self):
        """Return EXTRA information in a string"""

        results = []

        for key, value in self.__dict__.iteritems():
            #there are some attributes which I don't care about
            if key not in ['consequence_terms', 'amino_acids', 'cdna_end', 'cdna_start', 'cds_end', 'cds_start', 'codons', 'gene_id', 'transcript_id', 'protein_end', 'protein_start', 'variant_allele'] and value != None:
                results += ["%s=%s" %(key, value)]

        return ";".join(results)

class IntergenicConsequence():
    """A class to deal with intergenic consequences"""

    def __init__(self, intergenic_dict=None):
        self.variant_allele = None
        self.consequence_terms = []

        if intergenic_dict != None:
            for key, value in intergenic_dict.iteritems():
                setattr(self, key, value)

    def __reprstr(self):
        return "consequence_terms: %s" %(",".join(self.consequence_terms))

    def __repr__(self):
        return "%s.IntergenicConsequence instance at %s (%s)" %(self.__module__, hex(id(self)), self.__reprstr())

    def __str__(self):
        return "%s.IntergenicConsequence(%s)" %(self.__module__, self.__reprstr())


class Variant(ColocatedVariant):
    """A class to deal with variant"""

    def __init__(self, variant_dict=None):
        #Class attributes
        self.colocated_variants = []
        self.transcript_consequences = []
        self.intergenic_consequences = []
        self.most_severe_consequence = None
        self.seq_region_name = None

        #If you return a VEP record, define here the headers of that row
        self.header = ['#Uploaded_variation', 'Location', 'Allele', 'Gene', 'Feature', 'Feature_type', 'Consequence', 'cDNA_position', 'CDS_position', 'Protein_position', 'Amino_acids', 'Codons', 'Existing_variation', 'Extra']

        #Instantiate the class-base attributes
        ColocatedVariant.__init__(self)

        #the key to evaluate
        variant_keys = variant_dict.keys()

        if variant_dict != None:
            #Verify special attributes
            if variant_dict.has_key("colocated_variants"):
                self.colocated_variants = [ColocatedVariant(var) for var in variant_dict["colocated_variants"]]
                variant_keys.remove("colocated_variants")

            if variant_dict.has_key("transcript_consequences"):
                self.transcript_consequences = [TranscriptConsequence(tran) for tran in variant_dict["transcript_consequences"]]
                variant_keys.remove("transcript_consequences")

            if variant_dict.has_key("intergenic_consequences"):
                self.intergenic_consequences = [IntergenicConsequence(tran) for tran in variant_dict["intergenic_consequences"]]
                variant_keys.remove("intergenic_consequences")

            for key in variant_keys:
                value = variant_dict[key]
                setattr(self, key, value)

        #I can't have bot intergenic_consequences and transcript_consequences
        if len(self.intergenic_consequences) > 0  and len(self.transcript_consequences) > 0:
            raise VariantException, "I have both intergenic and transcript consequences for this variant"

    def __reprstr(self):
        colocated_variants = ",".join([var.id for var in self.colocated_variants])
        transcript_consequences = ["%s %s" %(tran.consequence_terms, tran.gene_id) for tran in self.transcript_consequences]
        transcript_consequences = ",".join(transcript_consequences)

        intergenic_consequences = ",".join(["%s" %(tran.consequence_terms) for tran in self.intergenic_consequences])

        #I can't have bot intergenic_consequences and transcript_consequences
        if len(self.intergenic_consequences) > 0  and len(self.transcript_consequences) > 0:
            raise VariantException, "I have both intergenic and transcript consequences for this variant"

        if transcript_consequences != '':
            returned_str = "id:%s; seq_region_name:%s; start:%s; end:%s; colocated_variants:%s; transcript_consequences:%s" %(self.id, self.seq_region_name, self.start, self.end, colocated_variants, transcript_consequences)

        else:
            returned_str = "id:%s; seq_region_name:%s; start:%s; end:%s; colocated_variants:%s; intergenic_consequences:%s" %(self.id, self.seq_region_name, self.start, self.end, colocated_variants, intergenic_consequences)

        return returned_str

    def __repr__(self):
        return "%s.Variant instance at %s (%s)" %(self.__module__, hex(id(self)), self.__reprstr())

    def __str__(self):
        return "%s.Variant(%s)" %(self.__module__, self.__reprstr())

    def getVariantAlleles(self):
        """Return a list of variant alleles for each consequence"""

        results = []

        for tran in self.transcript_consequences:
            results += [tran.variant_allele]

        return ",".join(results)

    def getExistingVariation(self):
        """Return existing variation id"""

        if len(self.colocated_variants) == 0:
            return None

        return ",".join([var.id for var in self.colocated_variants ])

    def getVEPRecord(self):
        """Return one or more VEP record a LIST"""

        #what I will return
        results = []

        #One or more record relying on how mano transcript_consequences
        if len(self.transcript_consequences) == 0:
            for tran in self.intergenic_consequences:
                line = [self.id, "%s:%s" %(self.seq_region_name, self.start), tran.variant_allele, None, None, None, ",".join(tran.consequence_terms), None, None, None, None, None, self.getExistingVariation(), None]
                results += [line]

        else:
            for tran in self.transcript_consequences:
                line = [self.id, "%s:%s" %(self.seq_region_name, self.start), tran.variant_allele, tran.gene_id, tran.transcript_id, "Transcript", ",".join(tran.consequence_terms), tran.cdna_start, tran.cds_start, tran.protein_start, tran.amino_acids, tran.codons, self.getExistingVariation(), tran.getExtraFeatures()]

                results += [line]

        return results

# A class to deal with input data
class QueryVEP():
    def __init__(self, inputfile=None, specie=None):
        """Instatiate the class. Inputfile and specie could be specified here. 
        Setting species via init method set the default specie"""
        
        self._offset = 50
        self._handle = None
        self._input = []
        self._results = []
        self._variants = []
        self._rest = REST.EndPoints.EnsEMBLEndPoint()
        self.specie = None

        if inputfile != None:
            self.Open(inputfile)
            
        if specie != None:
            self.specie = specie

    def setRESTserver(self, server):
        """Ovverride the default value of EnsEMBLEndPoint rest server"""
        self._rest.server = server

    def Open(self, inputfile):
        """Open a file for REST requests. Inputfile can be a file name or an open filehandle"""

        #Handle case
        if type(inputfile) == types.FileType:
            self._handle = inputfile

        elif type(inputfile) == types.StringType:
            self._handle = open(inputfile, "rU")
            
        elif inputfile.__module__ == "StringIO":
            #StringIO has the __iter__ method
            self._handle = inputfile

        else:
            raise VePException, "Cannot handle %s (%)" %(inputfile, type(inputfile))

    def Query(self, specie=None):
        """Performing query requests"""

        #Using the default specie if none
        if specie == None:
            specie = self.specie
            
        #A specie must be defined by the user a this point of code
        if specie == None:
            raise VePException, "A specie MUST be specified by __init__ or Query methods"

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
                self._queryREST(tmp_input, specie)

                #resetting tmp values
                tmp_input = []

        #Ensuring that all the requests were done
        if len(tmp_input) > 0:
            self._queryREST(tmp_input, specie)

        #Now trasform results in ensembl classes
        self._variants = []

        #Now cicle through each result and print a tuple. Write similar as VEP output
        for result in self._results:
            variant = Variant(result)
            logger.debug(variant)
            self._variants += [variant]


    def _queryREST(self, tmp_input, specie):
        """perform REST request"""
        
        #A specie must be defined by the user a this point of code
        if specie == None:
            raise VePException, "A specie MUST be specified by __init__ or Query methods"
        
        #perform a REST request
        tmp_variants = {'variants': tmp_input}

        logger.debug("Perform REST request")
        tmp_results = self._rest.getVariantConsequencesByMultipleRegions(species=specie, variants=tmp_variants, canonical=1, ccds=1, domains=1, hgvs=1, numbers=1, protein=1, xref_refseq=1)
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

    def CheckAssembly(self, assembly):
        """Check if assembly is the same specified by the user"""
        
        for var in self._variants:
            if var.assembly_name != assembly:
                #logging critical this message
                logger.critical("failed assembly version for %s (%s != %s)" %(var, var.assembly_name, assembly))
                raise VePException, "failed assembly version for %s (%s != %s)" %(var, var.assembly_name, assembly)
                
        
    


