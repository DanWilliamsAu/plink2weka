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

import csv


### CONSTANTS ###

# name of plink data set
DATA = 'testData/oddsRatioSet'

# some file extensions
ARFF = '.arff'
MAP = '.map'
PED = '.ped'
EXEMPLARS = '.exemplars'

# affection status (plink defaults)
UNAFFECTED = '1'
AFFECTED = '2'
MISSING = '-9'

# arff formatting strings
ATTRIBUTE = "@attribute {0} {{{1}}}\n"
RELATION = "@relation '{}'\n"
DATA_STRING = "@data\n"

### FUNCTIONS ###

def build_features(map_file):
    """ Create and return a dictionary, contianing each SNP in the plink data
    set.  Keys are the SNP name, the values are an empty set.
    Value Set will be expanded throughout course of program. 

    Also returns an ordered list of SNPs. Order is required for processing ped file.
    --map_file: the plink map data file

    """
    feature_dict = {}
    snp_list = []
    
    for line in map_file:
        currSNP = line.split()[1]
        feature_dict[currSNP] = set()
        snp_list.append(currSNP)
        
    return feature_dict, snp_list

     
def write_exemplars(ped_file, features, exemplars, snp_list):
    """ COMMENTS  """

    writer = csv.writer(exemplars, delimiter = ',')

    for line in ped_file:
        
        currLine = line.split()
        phenotype = currLine[5]
        # skip if the phenotype is missing - we only want those with pheno data
        if phenotype == MISSING:
            continue
        
        # process each line of the PED file in turn - output data to exemplar file
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
     
    exemplars.close()

    
def printable_attributes(genotype_set):
    """ takes a set and returns the contents of the set as a string,
    in a format required for the ARFF file """

    out = ''
    for item in genotype_set:
        out += item+','
    return out[:-1]


def write_arff_file(features, snp_list, arff):
    """ comment here """

    ## WRITE HEADER SECTION ## 

    # relation
    arff.write(RELATION.format(DATA))

    # attributes
    for snp in snp_list:
        attributes = printable_attributes(features[snp])
        arff.write(ATTRIBUTE.format(snp,attributes))
    arff.write(ATTRIBUTE.format('phenotype','1,2'))
    
    # data header
    arff.write(DATA_STRING)

    ## WRITE DATA SECTION ##
    exemplars = open(DATA + EXEMPLARS)
    for line in exemplars:
        arff.write(line)

    exemplars.close()
    arff.close()
    

    
def main():
    """ Open up files and run the program! """
    
    # open up the data files
    ped_file = open(DATA + PED)
    map_file = open(DATA + MAP)
    arff = open(DATA + ARFF, "w")
    exemplars = open(DATA + EXEMPLARS,"w")

    # build feature dictionary and snp_list
    features,snp_list = build_features(map_file)

    # write the examplars file
    write_exemplars(ped_file, features, exemplars, snp_list)
    
    # create the arff file
    write_arff_file(features, snp_list, arff)
    
main()
