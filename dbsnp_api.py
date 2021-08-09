# This script interacts with dbSnp via the efetch utility.

import json
import re
import requests
import time

DB_SNP = 'snp'

# dbsnp efetch max refsnp results:
MAX_DBSNP_QUERIES = 15

# dbsnp API min time between requests.
SLEEP_SECONDS = 3

SUBCOL_DELIM = ';'

# Given a dbSNP ID, fetches metadata about the SNP from dbSNP.
# Returns a dict of metadata including: 
# variant_type, disease_names, clincial significances, origins
def get_refsnps(snp_ids):
    start = 0
    stop = len(snp_ids)
    data = []
    while start < stop:
        cutoff = start + MAX_DBSNP_QUERIES
        cutoff = min(stop, cutoff)
        time.sleep(SLEEP_SECONDS)
        data_batch = _get_refsnps_internal(snp_ids[start:cutoff])
        data = data + data_batch
        start += MAX_DBSNP_QUERIES
    return data


# Wrapped to avoid exceeding API request/response size limitations.
def _get_refsnps_internal(snp_ids):
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    params = {
        'db': DB_SNP,
        'id': snp_ids,
        'rettype': 'json',
        'retmode': 'text',
    }

    data_dicts = []
    request = requests.get(url=url, params=params)
    parseable_json = '[{' + request.text[1:].replace('{"refsnp_id":', ',{"refsnp_id":') + ']'
    response = json.loads(parseable_json)
    for snp_response in response:
        data_dict = {}
        if 'primary_snapshot_data' not in snp_response:
            continue
        data = snp_response['primary_snapshot_data']
        data_dict['dbsnp_id'] = 'rs' + snp_response['refsnp_id']
        data_dict['dbsnp_variant_type'] = data['variant_type']
        data_dict['significances'] = set()
        data_dict['origins'] = set()
        data_dict['diseases'] = set()

        alleles = data['allele_annotations']
        for allele in alleles:
            if len(allele['clinical']) > 0:
                for clinical_data in allele['clinical']:
                    for clin_sig in clinical_data['clinical_significances']:
                        data_dict['significances'].add(clin_sig)
                    
                    for origin in clinical_data['origins']:
                        data_dict['origins'].add(origin)

                    for disease in clinical_data['disease_names']:
                        data_dict['diseases'].add(disease)
        data_dicts.append(data_dict)
        data_dict['significances'] = SUBCOL_DELIM.join(data_dict['significances'])
        data_dict['origins'] = SUBCOL_DELIM.join(data_dict['origins'])
        data_dict['diseases'] = SUBCOL_DELIM.join(data_dict['diseases'])
        
    return data_dicts


