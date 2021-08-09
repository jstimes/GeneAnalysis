#!/bin/bash

while getopts a:c:g:v: flag
do
    case "${flag}" in
        a) annotation_file=${OPTARG};;
	c) chromosome=${OPTARG};;
	g) gene=${OPTARG};;
	v) variants_file=${OPTARG};;
    esac
done

echo "Processing variants for: gene: $gene, annotation file: $annotation_file, chromosome: $chromosome".;

output_dir="./data/";

# First clean up any pre-existing outputs.
chr_str="chr${chromosome}";
find $output_dir -type f -name "${gene}*" -delete
find $output_dir -type f -name "${chr_str}*" -delete

# Extract chromosome from annotation file.
chr_annotation_file="${output_dir}${chr_str}_annotation.gff3";
awk -v chr=$chr_str {'if($1==chr)print $0'} $annotation_file | sed 's/chr//g' > $chr_annotation_file

echo "Wrote $chr_annotation_file.";

# Extract just gene of interest. 
# Writes an annotation file of entries for the gene.
# Writes bed files for the whole gene and one for the exons only.
python3 extract_gene.py $chr_annotation_file $gene $output_dir

# Extract variants just on chromosome of interest.
# First filter out variants on other chromosomes.
chr_variants_file="${output_dir}${chr_str}_variants.vcf"
awk -v chr=$chromosome {'if($1==chr)print $0'} $variants_file > $chr_variants_file

echo "Wrote ${chr_variants_file}.";

# Now append the dbSnp ID field to the info field to preserve it when converting to
# bed file format.
adjusted_variants_file="${output_dir}${chr_str}_variants_adjusted.vcf"
python3 adjust_vcf.py $chr_variants_file $adjusted_variants_file

chr_variants_bed_file="${output_dir}${chr_str}_variants.bed"
awk -v chr=$chromosome {'if($1==chr)print $1"\t"$2-1"\t"$2"\t"$8"\t.\t+"'} $adjusted_variants_file > $chr_variants_bed_file

echo "Wrote $chr_variants_bed_file.";

# Intersect variants and gene.
gene_bed_file="${output_dir}${gene}.bed"
gene_variants_file="${output_dir}${gene}_variants.bed"
./bedtools intersect -u -a $chr_variants_bed_file -b $gene_bed_file > $gene_variants_file

echo "Wrote $gene_variants_file.";

gene_exons_bed_file="${output_dir}${gene}_exons.bed"
gene_exons_variants_file="${output_dir}${gene}_exons_variants.bed"
./bedtools intersect -u -a $chr_variants_bed_file -b $gene_exons_bed_file > $gene_exons_variants_file

echo "Wrote $gene_exons_variants_file.";

# For each set of variants (whole gene & exon-only), analyze the data and
# generate a collated data file, distribution plots, & a text report.
whole_gene_output_file_prefix="${output_dir}${gene}_variants"
python3 analyze_variants.py $gene_variants_file $whole_gene_output_file_prefix

exons_only_output_file_prefix="${output_dir}${gene}_exons_variants"
python3 analyze_variants.py $gene_exons_variants_file $exons_only_output_file_prefix

# Finally, fetch data from dbsnp and dbvar about the gene to collect variant data
# that may not have been captured by the VCF file / gene annotation (e.g. 
# structural variants may start outside of the gene start/stop pos but still affect
# the gene).
python3 get_non_vcf_variants.py $gene $output_dir

echo "Finished.";

exit 0

