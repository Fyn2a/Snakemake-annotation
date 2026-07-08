import os

configfile: "config.yaml"


input_vcf = config["input_vcf"]
output_dir = config["output_dir"]
genome_build = config["genome_build"]


rule all:
    input:
        f"{output_dir}/final_results.csv"  # Final merged output file


rule bcftools_usage:  # extract the needed fields from the VCF into a CSV
    input:
        vcf = input_vcf
    output:
        csvFile = f"{output_dir}/temp.csv"
    shell:
        """
        bcftools query -f '%CHROM,%POS,%ALT,%INFO\\n' {input.vcf} > {output.csvFile}
        """


rule convert_csv_to_bed:
    input:
        bedcsv = f"{output_dir}/temp.csv"
    output:
        bedFile = f"{output_dir}/TEST-1_CNV1.cnv.bed"
    params:
        script2 = config["bed_script"]
    shell:
        """
        python {params.script2} --input {input.bedcsv} --output {output.bedFile}
        """
    threads: 6


rule classify_cnv:
    input:
        bed = f"{output_dir}/TEST-1_CNV1.cnv.bed"
    output:
        # ClassifyCNV writes Result.txt inside the --outdir directory
        result = f"{output_dir}/classifycnv_out/Result.txt"
    params:
        script = config["classifycnv_script"],
        outdir = f"{output_dir}/classifycnv_out"
    shell:
        """
        python3 {params.script} --infile {input.bed} --outdir {params.outdir} --GenomeBuild {genome_build}
        """
    threads: 6


rule convert_vcf_to_annovar:
    input:
        vcf = input_vcf
    output:
        av_input = f"{output_dir}/sample.cnv.avinput"
    params:
        annovar_dir = config["annovar_dir"]
    shell:
        """
        perl {params.annovar_dir}/convert2annovar.pl -format vcf4 {input.vcf} > {output.av_input}
        """
    threads: 6


rule run_annovar:
    input:
        avinput = f"{output_dir}/sample.cnv.avinput"
    output:
        # table_annovar.pl --csvout writes <outfile>.<build>_multianno.csv
        annovar = f"{output_dir}/annovar_results.{genome_build}_multianno.csv"
    params:
        annovar_dir = config["annovar_dir"],
        humandb = "humandb",
        outprefix = f"{output_dir}/annovar_results"
    shell:
        """
        perl {params.annovar_dir}/table_annovar.pl {input.avinput} {params.humandb} --buildver {genome_build} \
        --outfile {params.outprefix} --remove --protocol clinvar --operation f --nastring . \
        --polish --csvout
        """
    threads: 6


rule merge_results:
    input:
        classifycnv = f"{output_dir}/classifycnv_out/Result.txt",
        annovar = f"{output_dir}/annovar_results.{genome_build}_multianno.csv"
    output:
        merged = f"{output_dir}/final_results.csv"
    params:
        script = config["merge_script"]
    shell:
        """
        python3 {params.script} --classifycnv {input.classifycnv} --annovar {input.annovar} --output {output.merged}
        """
    threads: 6
