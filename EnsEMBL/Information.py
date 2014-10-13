# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 10:17:00 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A module to deal with information of EnsEMBL REST

"""

import REST.EndPoints
import Utils.helper

#The default exception
class InfoException(Exception) : pass

#the REST server module
EnsEMBLEndPoint = REST.EndPoints.EnsEMBLEndPoint()

#A class to deal with species
class Specie(Utils.helper.DummyClass):
    """A class to deal with species"""
    
    def __init__(self, *initial_data, **kwargs):
        Utils.helper.DummyClass.__init__(self, *initial_data, **kwargs)
        
    def __reprstr(self):
        return "name:%s; display_name:%s; assembly:%s" %(self.name, self.display_name, self.assembly)

    def __repr__(self):
        return "%s.Specie instance at %s (%s)" %(self.__module__, hex(id(self)), self.__reprstr())

    def __str__(self):
        return "%s.Specie(%s)" %(self.__module__, self.__reprstr())

class Assembly(Utils.helper.DummyClass):
    """A class to deal with assemblies"""
    
    def __init__(self, *initial_data, **kwargs):
        """You must specify the assembly dictionary and a name key to identify this object"""
        Utils.helper.DummyClass.__init__(self, *initial_data, **kwargs)
        
    def __reprstr(self):
        return "name:%s; assembly_name:%s; default_coord_system_version:%s" %(self.name, self.assembly_name, self.default_coord_system_version)

    def __repr__(self):
        return "%s.Assembly instance at %s (%s)" %(self.__module__, hex(id(self)), self.__reprstr())

    def __str__(self):
        return "%s.Assembly(%s)" %(self.__module__, self.__reprstr())


#a function to get the list of all available species
def getAvailableSpecies():
    """Return a lisf of all available species"""
    
    #perform a rest request
    results = EnsEMBLEndPoint.getAllAvailableSpecies()["species"]
    species = [Specie(result) for result in results]
    
    #Now get all the available common name
    names = [specie.name for specie in species]
    return names

def getSpecieByName(name):
    """Get a Specie Obj by name (whatever)"""
    
    #perform a rest request
    results = EnsEMBLEndPoint.getAllAvailableSpecies()["species"]
    species = [Specie(result) for result in results]
    
    for specie in species:
        if specie.name == name or specie.common_name == name or specie.display_name == name or name in specie.aliases:
            return specie
    
    #the default response if no name match
    raise InfoException, "Species %s not found" %(name)
    
#A function to get the assembly by name (whatever)
def getAssemblyByName(name):
    """A function to get the assembly by name (whatever)"""
    
    result = EnsEMBLEndPoint.getAssembliesBySpecie(species=name)
    assembly = Assembly(result, name=name)
    
    return assembly
    
