# -*- coding: utf-8 -*-
"""

Created on Tue Jul 15 14:52:21 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.it>

This project was inspired from git://github.com/gawbul/pyensemblrest.git and the
ensembl python example client (https://github.com/Ensembl/ensembl-rest/wiki/Example-Python-Client)
The main feature os those project are the generic definition of Rest methods by a config
file (pyensemblrest) and the definition of timeout for request in ensembl example.
The aim of this project is to merge those methodologies and to definie a library to
deal with ensembl REST api.

"""

import Config
import EndPoints

__author__ = "Paolo Cozzi"
__version__ = "0.2a"
__all__ = ["Config", "EndPoints"]

