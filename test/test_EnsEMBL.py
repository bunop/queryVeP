# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 14:35:16 2014

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

Testing ensembl modules

"""

import sys
import unittest

#Adding library modules path
sys.path.append("..")

#Define the SNPs used as the query

#"21 26960070 rs116645811 G A . . ."
snp1=dict(chrom=21,pos=26960070,id="rs116645811",ref="G",alt="A")

#"21 26965148 rs1135638 G A . . ."
snp2=dict(chrom=21,pos=26965148,id="rs1135638",ref="G",alt="A")

