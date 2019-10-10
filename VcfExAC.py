#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 6 06:20:27 2019
@author: manninm
This script takes a VCF file from the command line and annotates it using the ExAC REST API @ http://api.exac.hms.harvard.edu/requests
Args: a VCF file, and file name from user prompt via command line
Returns: A tab delimited text file with annotations for each variant (multiple allelic are decomposed into their own REST requests) 
Table includes Chromosome, Position, ReferenceAllele, Variant Effect, AltAllele, AlleleFreq, VarType, LociReadDepth, AlleleReadDepth, %VariantReads, %RefReads, RequestCall'

Relevant sources:
ExAC REST Api: http://exac.hms.harvard.edu/
VCF Version 4.2 Specifications: https://samtools.github.io/hts-specs/VCFv4.2.pdf
crash course in Variant Call Format: https://faculty.washington.edu/browning/intro-to-vcf.html 
crash course in python api: https://realpython.com/api-integration-in-python/
requests library videos:https://www.youtube.com/watch?v=QovKok-2u9k 
requests library guide: https://realpython.com/python-requests/#the-get-request
Json In Python: https://realpython.com/python-json/
"""
import sys
import requests
import json

def readSource(vcfFile):
	"""Reads in source file and formats for further use in other functions to construct table of VCF annotation 
	Args:VCF file
	Returns: 3 formated lists. One of Variant ID strings for bulk REST query, one of field information, one of variant information. All will be used to construct an annotation table"""
	with open(vcfFile,'r') as lines:
		restCalls=list()
		tabInfo=list()
		AlInfo=list()
		for line in lines:
			if line.startswith('#'): #skips over metasection of VCF file
				continue
		fields=line.strip().split('\t') #separating lines for iteration
		if ',' in fields[4]: #checking for multiple alternative alleles, if multiple alleles, will be in fifth column comma seperated
			alleles=fields[4].strip().split(',')
			info=fields[7].strip().split(';')
			genotype=fields[9].strip().split(':') #fetching genotype in column 10 ; sep GT:GQ:DP:AD:RO:QR:AO:QA:GL
			AO=genotype[6].strip().split(',') #fetch alt allele counts
			for allele in range(len(alleles)):
				getReq=fields[0].replace('chr','')+'-'+fields[1]+'-'+fields[3]+'-'+alleles[allele-1]
				restCalls.append(getReq)
				RO=genotype[4]
				DP=genotype[2]
				fieldInfo=fields[0]+'\t'+fields[1]+'\t'+fields[3]+alleles[allele-1]+'\t'
				AR=int(AO[allele])/int(DP) #Calculating percent reads confirming variant allele
				RR=int(AD)/int(DP) #calculating percent reads confirming ref allele
				alInfo=genotype[2]+'\t'+AO[allele]+str(AR)+'\t'+str(RR)+'\t'
				getReq='http://exac.hms.harvard.edu/rest/variant/ordered_csqs/'+fields[0].replace('chr','')+'-'+fields[1]+'-'+fields[3]+'-'+alleles[allele-1]
				restCalls.append(getReq)
				tabInfo.append(fieldInfo)	
				AlInfo.append(alInfo)
		else:
			getReq=fields[0].replace('chr','')+'-'+fields[1]+'-'+fields[3]+'-'+fields[4]
			info=fields[7].strip().split(';')
			genotype=fields[9].strip().split(';') #fetching genotype field GT:GQ:DP:AD:RO:QR:AO:QA:GL	
			fieldInfo=fields[0]+'\t'+fields[1]+'\t'+fields[3]+'\t'+fields[4]+'\t' #constructing table information and request call string	
			genotype=fields[9].strip().split(':')	
			AO=genotype[6]	
			AD=genotype[4]	
			DP=genotype[2]	
			AR=int(AO)/int(DP)	
			RR=int(AD)/int(DP)	
			alInfo=genotype[2]+'\t'+AO+'\t'+str(AR)+'\t'+str(RR)+'\t'	
			getReq='http://exac.hms.harvard.edu/rest/variant/ordered_csqs/'+fields[0].replace('chr','')+'-'+fields[1]+'-'+fields[3]+'-'+fields[4]	
			restCalls.append(getReq)	
			tabInfo.append(fieldInfo)	
			AlInfo.append(alInfo)	
		#print(AlInfo)	
		#print(restCalls)	
		#print(tabInfo)	
		#print(AlInfo)	
		return(tabInfo,restCalls,AlInfo)	
def RestRequest(RequestList):
	"""		
	Takes list of variant IDs for bulk query of REST API ExAC database 		
	Args: List of Variant IDs		
	Returns:List of allele frequencies and effects		
	"""		
	Req=RequestList
	calls=json.dumps(RequestList)
	VarEffect=list()					
	response=requests.post('http://exac.hms.harvard.edu/rest/bulk/variant',data=calls)
	json_data=json.loads(response.text)
	for id in Req:
		Con=list(json_data[calls[1]]['consequence'].keys())[1]
		Freq=(json_data.get(calls[1],{}).get('allele_freq'))
	
	return VarEffect	#GetEffect=		
		
		
		
		
		
			
def main():
	if len(sys.argv) < 1: #checks number of arguments and prompts user with usage if incorrect # provided
		sys.stderr.write("\nUSAGE: python " + sys.argv[0] + " VCF file > output\n\n")
		sys.exit(1)
	sourceFile=sys.argv[1] #passes trailing arguement to variable 
	calls=readSource(sourceFile) #passes arguement to function call and collects two lists as return values
	#GetEffect=
	RestRequest(calls)
	outputfile = input("Enter a file name: ") 
	with open(outputfile, mode="w", encoding="utf8" ) as fp: #constructing annotation table
		fp.write('Chromosome\tPosition\tReferenceAllele\tAltAllele\tVarEffect\tAlleleFreq\tVarType\tLociReadDepth\tAlleleReadDepth\t%VariantReands\t%RefReads\tRequestCall\n') #table needs a nice header!
		for info in range(len(tab)):
			item=tab[info-1]+'\t'+allele[info-1]+'\t'+calls[info-1]+'\n'
			fp.write(item)
if __name__ == '__main__': #allows for python interpreter to import as module as well as que from command line
        main()