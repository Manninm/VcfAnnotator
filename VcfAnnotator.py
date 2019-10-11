#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 6 06:20:27 2019
@author: manninm
This script takes a VCF file from the command line and annotates it using the ExAC REST API @ http://api.exac.hms.harvard.edu/requests by submitting a bulk query get post of variant IDs in json array

Args: a VCF file, and file name from user prompt via command line
Returns: A tab delimited text file with annotations for each variant (multiple allelic are decomposed into their own REST requests) 

Table includes Chromosome, Position, ReferenceAllele, AltAllele, VarEffect, AlleleFreq, Genes, Symbol, VarType, LociReadDepth, AlleleReadDepth, %VariantReands, %RefReads, RequestCall

Relevant sources:
ExAC REST Api: http://exac.hms.harvard.edu/
VCF Version 4.2 Specifications: https://samtools.github.io/hts-specs/VCFv4.2.pdf
crash course in Variant Call Format: https://faculty.washington.edu/browning/intro-to-vcf.html 
crash course in python api: https://realpython.com/api-integration-in-python/
requests library guide: https://realpython.com/python-requests/#the-get-request
Json In Python: https://realpython.com/python-json/
"""
import sys
import requests
import json
from openpyxl import Workbook
def readSource(vcfFile):
	"""Reads in source file and formats for further use in other functions to construct table of VCF annotation 
	Args:VCF file
	Returns: 3 formated lists. One of REST get requests, one of the allele information, one of variant information. All will be used to construct an annotation table"""
	with open(vcfFile,'r') as lines:
		restCalls=list()
		tabInfo=list()
		AlInfo=list()
		for line in lines: #for loop reads through lines of VCF and formats for later process
			if line.startswith('#'): #skips over metasection of VCF file
				continue
			fields=line.strip().split('\t') #separating lines for iteration by tab
			#print(fields)
			#print(len(fields))
			if ',' in fields[4]: #checking for multiple alternative alleles, if multiple alleles, will be in fifth column comma seperated
				alleles=fields[4].strip().split(',') # separating multiple alleles
				info=fields[7].strip().split(';') # 
				genotype=fields[9].strip().split(':') #fetching genotype in column 10 ; sep GT:GQ:DP:AD:RO:QR:AO:QA:GL
				AO=genotype[6].strip().split(',') #separating multiple allele counts (doesn't contain ref)
				for allele in range(len(alleles)): #get request call and table information for each alternative allele
					RO=genotype[4] #ref allele counts
					DP=genotype[2] #total read depth
					AR=int(AO[allele])/int(DP) #Calculating percent reads confirming variant allele
					RR=int(RO)/int(DP) #calculating percent reads confirming ref allele
					fieldInfo=fields[0]+'\t'+fields[1]+'\t'+fields[3]+alleles[allele-1]+'\t' #collecting info on variant chrom,position,ref and alt alleles
					alInfo=genotype[2]+'\t'+AO[allele]+str(AR)+'\t'+str(RR)+'\t' # collects read depth, variant depth, %AlleleReads, %RefReads
					getReq=fields[0].replace('chr','')+'-'+fields[1]+'-'+fields[3]+'-'+alleles[allele-1] #Collects variant ID for bulk query
					restCalls.append(getReq) #append values to empty lists for transfer to other functions
					tabInfo.append(fieldInfo)	
					AlInfo.append(alInfo)
					#print(AlInfo)
			else: #if not multi-allelelic do as above but no in forloop
				info=fields[7].strip().split(';')
				genotype=fields[9].strip().split(';') #fetching genotype field GT:GQ:DP:AD:RO:QR:AO:QA:GL
				fieldInfo=fields[0]+'\t'+fields[1]+'\t'+fields[3]+'\t'+fields[4]+'\t' #constructing table information and request call string
				genotype=fields[9].strip().split(':')
				AO=genotype[6]
				RO=genotype[4]
				DP=genotype[2]
				AR=int(AO)/int(DP)
				RR=int(RO)/int(DP)
				alInfo=genotype[2]+'\t'+AO+'\t'+str(AR)+'\t'+str(RR)+'\t'
				getReq=fields[0].replace('chr','')+'-'+fields[1]+'-'+fields[3]+'-'+fields[4]
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
	calls=json.dumps(RequestList) #convert list of IDS into json array
	VarEffect=list()					
	response=requests.post('http://exac.hms.harvard.edu/rest/bulk/variant/variant',data=calls) #bulk query post request
	json_data=json.loads(response.text) #converts json post data to a multi-embedded python dictionary
	for id in range(len(Req)):
		#print(Req[id-1])
		if 'vep_annotations' in json_data[Req[id-1]] and len(json_data[Req[id-1]]['vep_annotations']) > 0: #vep annotation was most complete in bulk query post return. Some variants do not have vep annotation must, and some have empty vep_annotations testing for both scenarios in one if/else statement
			symb=json_data[Req[id-1]]['vep_annotations'][0].get('SYMBOL')[0]
			Con=json_data[Req[id-1]]['vep_annotations'][0].get('major_consequence')#bulk consequence query post is 404:Not found, take major_consequence assuming first entry is most detrimental  variant
			Freq=json_data.get(Req[id-1],{}).get('allele_freq') #search dictionary for any value attached to allele_freq key
			Genes=json_data[Req[id-1]]['genes'][0]
			var=Con+'\t'+str(Freq)+'\t'+Genes+'\t'+symb
			VarEffect.append(var)
		else: #some variants have missing vep_annotations, if they fail the above if statement, these entries will be empty/not found
			symb='NULL'
			Con='NULL'
			Freq="NULL"
			Genes='NULL'
			var=Con+'\t'+str(Freq)+'\t'+Genes+'\t'+symb
			VarEffect.append(var)
	return(VarEffect)
		
def main():
	if len(sys.argv) < 1: #checks number of arguments and prompts user with usage if incorrect # provided
		sys.stderr.write("\nUSAGE: python " + sys.argv[0] + " VCF file > output\n\n")
		sys.exit(1)
	sourceFile=sys.argv[1] #passes trailing arguement to variable
	tab,calls,allele=readSource(sourceFile) #passes arguement to function call and collects 3 lists as return values
	GetEffect=RestRequest(calls) #passes list of bulk query IDs to RestRequest() function
	outputfile = input("Enter a file name: ") #prompts user to enter file name from command line, prevents overwriting previous files
	with open(outputfile, mode="w", encoding="utf8" ) as fp: #constructing annotation table
		fp.write('Chromosome\tPosition\tReferenceAllele\tAltAllele\tVarEffect\tAlleleFreq\tGenes\tSymbol\tVarType\tLociReadDepth\tAlleleReadDepth\t%VariantReands\t%RefReads\tRequestCall\n') #table needs a nice header!
		for info in range(len(tab)):
			item=tab[info-1]+GetEffect[info-1]+'\t'+allele[info-1]+'\t'+calls[info-1]+'\n'
			fp.write(item)
if __name__ == '__main__': #allows for python interpreter to import as module as well as que from command line
        main()