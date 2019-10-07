#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 6 06:20:27 2019
@author: manninm

Relevant sources:
ExAC REST Api: http://exac.hms.harvard.edu/
VCF Version 4.2 Specifications: https://samtools.github.io/hts-specs/VCFv4.2.pdf
crash course in Variant Call Format: https://faculty.washington.edu/browning/intro-to-vcf.html 
crash course in python api: https://realpython.com/api-integration-in-python/
requests library videos:https://www.youtube.com/watch?v=QovKok-2u9k 
requests library guide: https://realpython.com/python-requests/#the-get-request
"""
import sys
import requests

def readSource(vcfFile):
	"""Reads in source file and formats for further use in other functions to construct table of VCF annotation 
	Args:VCF file
	Returns: a formated string """
	with open(vcfFile,'r') as lines:
		for line in lines:
			if line.startswith('#'): #skips over comment section of gff file
				continue
			fields=line.strip().split('\t')
			print(fields)







def main():
	sourceFile=sys.argv[1]
	readSource(sourceFile)

if __name__ == '__main__':
        main()