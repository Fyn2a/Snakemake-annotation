# annotation

A [Snakemake](https://snakemake.readthedocs.io/) workflow that annotates copy-number
variants (CNVs) from a VCF by combining two independent annotations:

- **ClassifyCNV** — ACMG clinical classification of each CNV.
- **ANNOVAR** — gene / ClinVar annotation of the same intervals.

The two result sets are merged on their `Start`/`End` coordinates into a single
`final_results.csv`.

## Pipeline

```
input VCF
  |
  |-- bcftools query ............ temp.csv        (CHROM,POS,ALT,INFO)
  |     '-- vcf2bed.py ........... TEST-1_CNV1.cnv.bed
  |           '-- ClassifyCNV .... classifycnv_out/Result.txt
  '-- convert2annovar.pl ........ sample.cnv.avinput
        '-- table_annovar.pl ..... annovar_results.hg19_multianno.csv

          merge.py (Start/End inner join) -> final_results.csv
```

## Layout

| File | Purpose |
|------|---------|
| `Snakefile.smk` | Workflow definition (the DAG above) |
| `config.yaml` | Paths and genome build |
| `vcf2bed.py` | Converts the bcftools CSV to a BED file |
| `merge.py` | Merges ClassifyCNV + ANNOVAR outputs |
| `environment.yaml` | Conda environment for the pip/conda-installable deps |
| `input/TEST-1_CNV1.cnv.vcf` | Small demo CNV VCF (hg19) |

## External tools (not bundled)

ANNOVAR and ClassifyCNV cannot be installed from conda/pip:

- **ANNOVAR** — register and download from <https://annovar.openbioinformatics.org>,
  unpack to `annovar/`, and download the `clinvar` database into `humandb/`.
- **ClassifyCNV** — `git clone https://github.com/Genotek/ClassifyCNV` into `ClassifyCNV/`
  and run its `update_clinvar.sh` once.

Update the paths in `config.yaml` if you place them elsewhere.

## Run

```bash
conda env create -f environment.yaml
conda activate annotation
snakemake -s Snakefile.smk --cores 6
```

The merged annotation lands at `FinalOUT/final_results.csv`.
