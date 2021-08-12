### Variant analysis


#### Overview

This is a pipeline that generates variant data and synthesizes some figures and 
reports based on that data. It uses a genome annotation file and whole genome VCF file as input, and then, given a gene of interest, computes details about variants associated with that gene. This software utilizes the BEDTools software (Quinlan, 2010) and some open source python packages listed below.


#### Datasets

**Human genome assembly**: GRCh37

**Genome annotation**: From gencode, release 19 ([http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_19/](http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_19/))

**Genome variants**: 1000 genomes phase 1 analysis ([https://ftp-trace.ncbi.nih.gov/1000genomes/ftp/phase1/analysis_results/integrated_call_sets/](https://ftp-trace.ncbi.nih.gov/1000genomes/ftp/phase1/analysis_results/integrated_call_sets/))

**External databases**: dbsnp and dbvar via eutilities ([https://www.ncbi.nlm.nih.gov/snp/docs/eutils_help/](https://www.ncbi.nlm.nih.gov/snp/docs/eutils_help/)).


#### Pipeline Steps

The file `run.sh` runs this analysis pipeline. Data inputs and outputs are expected to be loaded from / written to the ‘data’ folder. The input flags are as follows:



* -a: The genome **a**nnotation file to use.
* -c: The **c**hromosome number of interest
* -g: The **g**ene of interest
* -v: The variants VCF file to use.

&lt;gene> and &lt;chr> below refer to the values used for the -g and -c flags respectively.

The pipeline follows these steps:



1. Cleans pre-existing output from the ‘data’ folder.
2. Extracts the genome annotations just for the chromosome of interest.
    1. Written to _chr&lt;chr>_annotation.gff3_
3. Extracts the genome annotations just for the gene of interest, and also generates bed files representing these annotations; one for the whole gene and one just for exons.
    2. Gene annotations written to _&lt;gene>.gff3_
    3. Gene bed file written to _&lt;gene>.bed_
    4. Exons bed file written to _&lt;gene>_exons.bed_
4. Extracts the variants only on the chromosome of interest.
    5. Filtered VCF file written _&lt;chr>_variants.vcf_
    6. Modified VCF file with the INFO column containing the dbSnp ref written to _chr&lt;chr>_variants_adjusted.vcf_
    7. Variants on chromosome bed file written to _chr&lt;chr>_variants.bed_
5. Computes gene and variant intersections.
    8. Whole gene and variant intersections written to _&lt;gene>_variants.bed_
    9. Exon-only variant intersections written to _&lt;gene>_exons_variants.bed_
6. Cleans the intersection data, joining it with dbSnp annotations where possible; generates plots and a text report based on this data.
    10. Whole-gene variant dataset written to _&lt;gene>_variants.csv_
    11. Allele frequency distribution plot written to _&lt;gene>_variants_af_distribution.png_
    12. Variant type distribution plot written to _&lt;gene>_variants_variant_type_distribution.png_
    13. A text report summarizing some findings is written to _&lt;gene>_variants_report.txt_
    14. Exon-only equivalents are written to files with the prefix _&lt;gene>_exons__
7. Generates another set of data based solely on dbsnp & dbvar data (i.e. not just variants defined in the VCF file that overlap with the gene’s annotation; looks up all pathogenic dbsnp and dbvar entries associated with the gene of interest).
    15. Pathogenic dbsnp variant data written to _&lt;gene>_pathogenic_snps.csv_
    16. Pathogenic dbvar variant data written to _&lt;gene>_pathogenic_svs.csv_


#### Pipeline Outputs

**&lt;gene>_variants.csv & &lt;gene>_exons_variants.csv _columns:**



* _chr_: the chromosome of interest
* _start_: start position of this variant in the chromosome, in reference to the human genome assembly defined above.
* _stop_: stop position of this variant.
* _allele frequency_: The reported allele frequency in the VCF file (AF=).
* _variant type_: The variant type as reported in the VCF file.
* _dbsnp id_: ID of the snp in dbSnp. This can be pasted into the dbSnp search bar for finding more information about the variant.
* _dbsnp_variant_type_: The variant type as reported by dbSnp. This is slightly more specific than the VCF variant type (e.g. this reports ‘del’ instead of ‘indel’).
* _significances_: This column includes any pathogenic metadata about the variant from dbSnp; empty if no metadata about this present in dbSnp. Values include: 
    * 'pathogenic-likely-pathogenic', 'drug-response', 'likely-benign', 'likely-pathogenic', 'pathogenic', 'risk-factor', 'not-provided', 'uncertain-significance', 'benign-likely-benign', 'benign', 'conflicting-interpretations-of-pathogenicity'
* _origins_: dbSnp reported origin of variant. Values include: 
    * 'unknown', 'maternal', 'somatic', 'germline'
* _diseases_: dbSnp reported diseases associated with this variant. 

The columns of **&lt;gene>_pathogenic_snps.csv _**are a subset of those in **&lt;gene>\_variants.csv.**

The columns of **_&lt;gene>_pathogenic_svs.csv_** are similar to those of **_&lt;gene>_pathogenic_snps.csv_**, except _dbsnp_id _is replaced with _dbvar_id_ and _variant_type_ refers to the dbVar reported variant type.


#### Usage Instructions

_Prerequisite: you must be using a UNIX environment to run this analysis._



1. Create a new directory and download the source code.
2. Ensure python3 is installed and install bedtools
    1. Python3 is likely already installed, but see these docs for any help:
        1. [https://docs.python.org/3/using/unix.html](https://docs.python.org/3/using/unix.html)
    2. For bedtools, you can either download and build the source as described below, or directly download the bedtools binary here:
        2. [https://github.com/arq5x/bedtools2/releases/download/v2.30.0/bedtools.static.binary](https://github.com/arq5x/bedtools2/releases/download/v2.30.0/bedtools.static.binary)
        3. Build from source:

            ```
            wget -cd https://github.com/arq5x/bedtools2/archive/master.zip

            unzip master.zip

            cd bedtools2-master/

            sudo yum -y install gcc-c++

            sudo yum -y install zlib-devel

            make

            ```

3. Install python3 package dependencies:
    3. If pip is not already installed, run:
        4. sudo apt install python3-pip
    4. Run `pip install x` for each of these packages:
        5. pandas
        6. requests
        7. biopython
        8. numpy
        9. matplotlib
4. Change into the `variant_analysis` directory.
5. Download input data files to the ‘data’ directory:
    5. _gencode.v19.annotation.gff3_
        10. Download and uncompress this file (or a different version) from here:
        11. [http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_19/](http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_19/)
    6. _ALL.wgs.integrated_phase1_v3.20101123.snps_indels_sv.sites.vcf_
        12. Download and uncompress this file (or a different version) from here:
        13. [https://ftp-trace.ncbi.nih.gov/1000genomes/ftp/phase1/analysis_results/integrated_call_sets/](https://ftp-trace.ncbi.nih.gov/1000genomes/ftp/phase1/analysis_results/integrated_call_sets/)
6. Mark the bash script as executable:

    ```
    chmod +x run.sh

    ```

7. Before you can run the script, you’ll need to know your gene of interest and the chromosome number it is on. You can type in your gene name at UCSC Genome Browser to find its chromosome:

    [http://genome.ucsc.edu/cgi-bin/hgGateway](http://genome.ucsc.edu/cgi-bin/hgGateway)

8. If everything has been installed and the input data is present, you can run the pipeline using the following command:

    ```
    ./run.sh -a data/gencode.v19.annotation.gff3 -g <gene> -c <chromosome_number> -v data/ALL.wgs.integrated_phase1_v3.20101123.snps_indels_sv.sites.vcf
```

Replacing &lt;gene> and &lt;chromosome_number> with your own choices, and 

remembering to update the data file paths if you downloaded different data to begin with.



9. The script will output “Finished” when it completes; some steps such as fetching results from dbsnp/dbvar can take some time to complete.




