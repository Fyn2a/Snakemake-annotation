import pandas as pd
import argparse

def merge_results(classifycnv_file, annovar_file, output_file):
    # ClassifyCNV writes a tab-separated Result.txt
    classifycnv_df = pd.read_csv(classifycnv_file, sep='\t')
    # ANNOVAR --csvout produces a comma-separated *.multianno.csv
    annovar_df = pd.read_csv(annovar_file)
    merged_df = pd.merge(classifycnv_df, annovar_df, on=['Start', 'End'], how='inner')
    merged_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge classifyCNV and ANNOVAR results")
    parser.add_argument("--classifycnv", required=True, help="Path to classifyCNV Result.txt")
    parser.add_argument("--annovar", required=True, help="Path to ANNOVAR multianno.csv")
    parser.add_argument("--output", required=True, help="Path to merged output file")
    args = parser.parse_args()
    merge_results(args.classifycnv, args.annovar, args.output)
