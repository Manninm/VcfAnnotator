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
	Returns: two formated lists. One of REST get requests, and one of the variant infor used to construct the requests. Both will be used to construct an annotation table"""
	with open(vcfFile,'r') as lines:
		restCalls=list()
		tabInfo=list()
		for line in lines:
			if line.startswith('#'): #skips over comment section of VCF file
				continue
			fields=line.strip().split('\t') #separating lines for iteration
			#print(fields)
			#print(len(fields))
			if ',' in fields[4]: #checking for multiple alternative alleles
				alleles=fields[4].strip().split(',')
				for allele in range(len(alleles)): #get request call and table information for each alternative allele
					fieldInfo=fields[0]+'\t'+fields[1]+'\t'+fields[3]+'\t'+alleles[allele-1]+'\t'
					getReq='api.http://exac.hms.harvard.edu/rest/variant/'+fields[0].replace('chr','')+'-'+fields[1]+'-'+fields[3]+'-'+alleles[allele-1]
					restCalls.append(getReq)
					tabInfo.append(fieldInfo)
			else:
				fieldInfo=fields[0]+'\t'+fields[1]+'\t'+fields[3]+'\t'+fields[4]+'\t' #constructing table information and request call string
				getReq='api.http://exac.hms.harvard.edu/rest/variant/'+fields[0].replace('chr','')+'-'+fields[1]+'-'+fields[3]+'-'+fields[4]
				tabInfo.append(fieldInfo)
				restCalls.append(getReq)
		#print(restCalls)
		#print(tabInfo)
		return(tabInfo,restCalls)



def main():
	if len(sys.argv) < 1:
		sys.stderr.write("\nUSAGE: python " + sys.argv[0] + " VCF file > output\n\n")
		sys.exit(1)
	sourceFile=sys.argv[1]
	tab,calls=readSource(sourceFile)
	outputfile = input("Enter a file name: ") 
	with open(outputfile, mode="w", encoding="utf8" ) as fp:
		fp.write('Chromosome\tPosition\tReferenceAllele\tAltAllele\tRequestCall\n')
		for info in range(len(tab)):
			item=tab[info-1]+calls[info-1]+'\n'
			fp.write(item)
if __name__ == '__main__':
        main()