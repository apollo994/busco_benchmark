#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import pandas as pd
import requests
from lxml import etree
import time


# see
# https://github.com/guigolab/geneid-parameter-files
# for an example on how to set up this script
parameter_files_matrix = "https://raw.githubusercontent.com/guigolab/geneid-parameter-files/main/matrix.tsv"
parameter_files_location = "https://raw.githubusercontent.com/guigolab/geneid-parameter-files/main/parameter_files"



# Define an alternative in case everything fails
selected_param = "Homo_sapiens.9606.param"

data = pd.read_csv(parameter_files_matrix, sep = "\t")

def split_n_convert(x):
    return [int(i) for i in x.replace("'", "").strip("[]").split(", ")]

data.loc[:,"taxidlist"] = data.loc[:,"taxidlist"].apply(split_n_convert)

###
# Separate the lineages into a single taxid per row
###
exploded_df = data.explode("taxidlist")
exploded_df.columns = ["species", "taxid_sp", "parameter_file", "taxid"]
exploded_df.loc[:,"taxid"] = exploded_df.loc[:,"taxid"].astype(int)


NCBI_RESPONSE_MAPPER = {
    'lineage': 'taxidlist',
    'tax_id':'taxid',
    'organism_name':'species'
}

def get_taxon_from_ENA(taxid):
    taxon = dict()
    try:
        response = requests.get(f"https://www.ebi.ac.uk/ena/browser/api/xml/{taxid}")
        xml = response.content
        if not xml or len(xml) == 0:
            return taxon
        root = etree.fromstring(xml)
        for child in root:
            child_taxid = int(child.attrib["taxId"])
            if(child_taxid == taxid):
                lineage = []
                for taxon_node in child:
                    if taxon_node.tag == 'lineage':
                        lineage.append(int(child.attrib["taxId"]))
                        lineage.extend([int(node.attrib['taxId']) for node in taxon_node])
                        taxon['lineage'] = lineage
                        taxon['taxid'] = child_taxid
                        taxon['species'] = child.attrib['scientificName']
                        break
        return taxon
    except:
        return taxon
    
def get_taxon_from_NCBI(taxid):
    taxon = dict()
    try:
        response = requests.get(f"https://api.ncbi.nlm.nih.gov/datasets/v1/taxonomy/taxon/{taxid}")
        if not response.json() or not 'taxonomy_nodes' in response.json():
            return taxon
        taxon_to_insert = response.json()['taxonomy_nodes'][0]['taxonomy']
        for k in NCBI_RESPONSE_MAPPER.keys():
            value = NCBI_RESPONSE_MAPPER[k]
            taxon[value] = taxon_to_insert[k]
        return taxon
    except:
        return taxon

def get_lineage_from_taxid(new_taxid):
    counter = 0
    if counter > 2:
        time.sleep(1)
    taxon = get_taxon_from_NCBI(new_taxid)
    if not taxon:
        taxon = get_taxon_from_ENA(new_taxid)
        if not taxon:
            counter += 1
            #skip taxon if does not exists in ncbi
            return None
    if taxon['taxidlist'][0] == 1:
        taxon['taxidlist'].reverse()
    return taxon['taxidlist']


# taxid of interest
target_taxid = sys.argv[1]
target_lineage = get_lineage_from_taxid(target_taxid)


###
# Get the species of interest lineage
###

query = pd.DataFrame(target_lineage)
query.columns = ["taxid"]
query.loc[:,"taxid"] = query.loc[:,"taxid"].astype(int)

###
# Intersect the species lineage with the dataframe of taxids for parameters
###
intersected_params = query.merge(exploded_df, on = "taxid")

###
# If there is an intersection, select the parameter whose taxid appears
#   less times, less frequency implies more closeness
###
if intersected_params.shape[0] > 0:

	taxid_closest_param = intersected_params.loc[:,"taxid"].value_counts().sort_values().index[0]

	selected_param = intersected_params[intersected_params["taxid"] == taxid_closest_param].loc[:,"parameter_file"].iloc[0]

# print(target_taxid)
print(f"{parameter_files_location}", selected_param, sep = "/", end = "")


