##############################################################################
#
# Program Name:
#
# plink2weka
#
# Program description:
#
# Program for creating weka ARFF files from plink datasets.  Weka is a
# machine learning program.  This program reformats plink data into ARFF 
# format.  That is, it creates an ARFF file where each SNP in the PLINK data
# becomes a feature, and each individual in the PLINK data becomes an
# examplar.
#
# For more on weka and the ARFF format see: 
# http://www.cs.waikato.ac.nz/ml/weka/arff.html
#
# Usage:
#
#
# Author:
#
# Daniel Williams (Department of Psychiatry, University of Melbourne)
#                 daniel.williams@unimelb.edu.au
#
# Date Created:
#
# 26 November 2013
#
##############################################################################

import csv, sys, argparse


### CONSTANTS ###

# some file extensions
ARFF = '.arff'
MAP = '.map'
PED = '.ped'
examplarS = '.examplars'

# affection status (plink defaults)
UNAFFECTED = '1'
AFFECTED = '2'
MISSING = '-9'

# arff formatting strings
ATTRIBUTE = "@attribute {0} {{{1}}}\n"
RELATION = "@relation '{}'\n"
DATA_STRING = "@data\n"

# argparse strings
DATASET_HELP = \
"name of plink dataset that you wish to convert to weka arff file"
VALIDATE_SET_HELP = \
"use if you have a second plink dataset and you want to create \
an arff consistent with dataset"

# UI strings
WRITING = "Writing {0} file for {1}....."
DONE = "Done!"
CREATED = "{0}.{1} has been created"


### FUNCTIONS ###

def process_commands():
    """ Build the command line argument parser and use it
    to return the parsed arguments from the command line.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", help=DATASET_HELP)
    parser.add_argument("--validate", help=VALIDATE_SET_HELP, type=str)
    return parser.parse_args()

def get_filename():
    """ checks command line arguments and returns name of
    PLINK bim file which is to be converted
    if supplied or defualt file if not """

    if len(sys.argv) != 2:
        print "please provide a dataset name. Usage:"
        print "python plink2weka.py <dateset>"
        print "e.g. if you have schizophrenia.ped and schizophrenia.map"
        print "type python plink2weka.py schizophrenia" 
        sys.exit()
    else:
        return sys.argv[1]

def build_features(map_file):
    """ Create and return a dictionary, contianing each SNP in the plink data
    set.  Keys are the SNP name, the values are an empty set.
    Value Set will be expanded throughout course of program. 

    Also returns an ordered list of SNPs. Order is required for processing
    ped file.
    
    --map_file: the plink map data file

    """
    
    feature_dict = {}
    snp_list = []
    
    for line in map_file:
        currSNP = line.split()[1]
        feature_dict[currSNP] = set(['00'])
        snp_list.append(currSNP)

    return feature_dict, snp_list

     
def write_examplars(ped_file, features, examplars, snp_list):
    """ Creates and writes to the file .examplar, where each line on the file
    is an individual, made up of attributes, where each attribute is
    the genotype of that individual at a particular SNP.  Also builds up
    the features dictionary, where the key is a set of possible genotypes.

    ped_file -- the ped file object, which contains genotype data
    features -- the dictionary of SNPs and genotype sets
    examplars -- file object for the exmplar file.
    snp_list -- ordered list of SNPs
    """

    
    writer = csv.writer(examplars, delimiter = ',')

    for line in ped_file:
        
        currLine = line.split()
        phenotype = currLine[5]
        # skip if the phenotype is missing - we only want those with pheno data
        if phenotype == MISSING:
            continue
        
        # process each line of the PED file in turn - output data to examplar file
        # and build up different alleles for each file
        currLine = currLine[6:]
        outline = []
        i = 0; j = 0
        while i < len(currLine):
            currSNP = currLine[i]+currLine[i+1]
            outline.append(currSNP)
            features[snp_list[j]].add(currSNP)
            i += 2; j += 1

        # assert the current line has the correct number of SNPs
        assert(len(outline) == len(features))

        # add phenotype to data
        outline.append(phenotype)
        
        # write to file
        writer.writerow(outline)
     
    examplars.close()
    return features

    
def printable_attributes(genotype_set):
    """ takes a set and returns the contents of the set as a string,
    in a format required for the ARFF file """

    out = ''
    for item in genotype_set:
        out += item+','
    return out[:-1]


def write_arff_file(features, snp_list, arff, data):
    """ Writes the arff file in the format requried by weka. First creates
    the header section, which lists the attributes, and then writes the
    data section, which is reproduced from the examplar file, created
    earlier in the program.

    data -- the name of the dataset, used to correctly name the arff file
    features -- the dictionary of SNPs and genotype sets
    snp_list -- ordered list of SNPs
    arff - arff file object, for writing the file
    """

    ## WRITE HEADER SECTION ## 
    # relation
    arff.write(RELATION.format(data))

    # attributes
    for snp in snp_list:
        attributes = printable_attributes(features[snp])
        arff.write(ATTRIBUTE.format(snp,attributes))
    arff.write(ATTRIBUTE.format('phenotype','1,2'))
    
    # data header
    arff.write(DATA_STRING)

    ## WRITE DATA SECTION ##
    examplars = open(data + examplarS)
    for line in examplars:
        arff.write(line)

    examplars.close()
    arff.close()
    
def initialise_files(dataset_name):
    """ returns the file objects needed for the program """
    ped_file = open(dataset_name + PED)
    map_file = open(dataset_name + MAP)
    arff = open(dataset_name + ARFF, "w")
    examplars = open(dataset_name + examplarS,"w")
    return (ped_file, map_file, arff, examplars)

 
def main():
    """ Open up files and run the program! """
    
    # open up the data files
    args = process_commands()
    data = args.dataset
    ped_file, map_file, arff, examplars = initialise_files(data)

    if args.validate:
        validate_data = args.validate
        vped_file, vmap_file, varff, vexamplars = initialise_files(validate_data)

    # build feature dictionary and snp_list
    
    features,snp_list = build_features(map_file)
    
    # write the examplars file(s)
    print WRITING.format("examplar", data),
    features = write_examplars(ped_file, features, examplars, snp_list)
    print DONE
    print CREATED.format(data, "examplar")
    
    if args.validate:
        print WRITING.format("examplar", validate_data),
        features = write_examplars(vped_file, features, vexamplars, snp_list)
        print DONE
        print CREATED.format(validate_data, "examplar")
        
    # create the arff file
    print WRITING.format("arff", data),
    write_arff_file(features, snp_list, arff, data)
    print DONE
    print CREATED.format(data, "arff")
    if args.validate:
        print WRITING.format("arff", data),
        write_arff_file(features, snp_list, varff, validate_data)
        print DONE
        print CREATED.format(data,"arff")
main()
