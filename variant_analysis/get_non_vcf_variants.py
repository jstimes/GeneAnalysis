# Given a gene, looks up entries in dbVar and dbSnp for that gene
# and writes the results to a file.
# This is intended to augment the set of variants defined in the original
# VCF file.

from dbsnp_api import get_refsnps
from Bio import Entrez
import pandas as pd
import json
import requests
import sys
import xml.etree.ElementTree as ET


# INPUT ARGUMENTS #######################################

# Gene name to study.
gene = sys.argv[1]

# Output file path prefix to use.
output_path_prefix = sys.argv[2]

#########################################################

Entrez.email = 'jacob.stimes@gmail.com'

DB_SNP = 'snp'
DB_VAR = 'dbvar'

# Searches a genetic variant DB for the given gene, returning a list of 
# pathogenic variant reference IDs found for that gene.
def get_pathogenic_variants_for_gene(db, gene):
    query = Entrez.esearch(db=db, 
            term=f'{gene}[Gene Name] AND pathogenic[Clinical_Significance]')

    results = Entrez.read(query)
    ids = results['IdList']
    return ids


# XML tags used in the dbvar esummary results
SUMMARY_TAG = 'DocumentSummary'
ID_TAG = 'SV'
SIGNIFICANCE_TAG = 'dbVarClinicalSignificanceList'
TYPE_TAG = 'dbVarVariantTypeList' 
HUMAN_GENOME_ASSEMBLY = 'GRCh37'
ASSEMBLY_TAG = 'Assembly'
CHR_START_TAG = 'Chr_start'
CHR_END_TAG = 'Chr_end'
CHR_TAG = 'Chr'


# Given a list of SV IDs from dbVar, fetch summaries from them and return relevant
# metadata via a list of dicts (one dict per SV).
def get_refsvs(sv_ids):
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
    id_value = ','.join(sv_ids)
    params = {
        'db': DB_VAR,
        'id': f'{id_value}',
        'rettype': 'json',
        'retmode': 'text',
    }

    request = requests.get(url=url, params=params)
    
    data_dicts = []
    root = ET.ElementTree(ET.fromstring(request.text)).getroot()
    for summary in root.iter(SUMMARY_TAG):
        data_dict = {}
        # Capture some metadata.
        data_dict['dbvar_id'] = summary.find(ID_TAG).text
        data_dict['significances'] = summary.find(SIGNIFICANCE_TAG).find('string').text
        data_dict['variant_type'] = summary.find(TYPE_TAG).find('string').text

        # Add variants position data.
        locations_list_tag = 'dbVarPlacementList'
        location_tag = 'dbVarPlacement'
        for location in summary.find(locations_list_tag).iter(location_tag):
            # Summary contains location data for multiple assemblies.
            if location.find(ASSEMBLY_TAG).text == HUMAN_GENOME_ASSEMBLY:
                data_dict['chr'] = location.find(CHR_TAG).text
                data_dict['start'] = location.find(CHR_START_TAG).text
                data_dict['end'] = location.find(CHR_END_TAG).text
        data_dicts.append(data_dict)
    return data_dicts


sv_ids = get_pathogenic_variants_for_gene(DB_VAR, gene)
sv_data = get_refsvs(sv_ids)
sv_df = pd.DataFrame(sv_data)
sv_output_file = f'{output_path_prefix}{gene}_pathogenic_svs.csv'
sv_df.to_csv(sv_output_file, index=False)
print(f'Wrote {sv_output_file}.')

snp_ids = get_pathogenic_variants_for_gene(DB_SNP, gene)
snp_data = get_refsnps(snp_ids)
snp_df = pd.DataFrame(snp_data)
snp_output_file = f'{output_path_prefix}{gene}_pathogenic_snps.csv'
snp_df.to_csv(snp_output_file, index=False)
print(f'Wrote {snp_output_file}.')

