import pandas as pd
from fuc import pybed
import argparse

def end_position(value: str):
    if 'END=' in value:
        try:
            end_value = next(part.split('=')[1] for part in value.split(';') if part.startswith('END='))
            return int(end_value)
        except (ValueError, StopIteration):
            return pd.NA
    return pd.NA

def extract_info(cnv_file: str, bed_file: str):
    # bcftools query emits no header row, so read positionally.
    df = pd.read_csv(cnv_file, header=None)

    chrom = df.iloc[:, 0]
    # VCF POS is 1-based; BED start is 0-based half-open.
    start = df.iloc[:, 1].astype(int) - 1
    alt = df.iloc[:, 2].str.replace(r'^<|>$', '', regex=True)
    info = df.iloc[:, 3]

    end_pos = info.apply(end_position)

    new_df = pd.DataFrame({
        'Chromosome': chrom,
        'Start': start,
        'End': end_pos,
        'Type': alt
    })
    # Drop records without a usable END and keep End as an integer column.
    new_df = new_df.dropna(subset=['End'])
    new_df['End'] = new_df['End'].astype(int)

    bed = pybed.BedFrame.from_frame(data=new_df, meta=[])
    bed.to_file(bed_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CSV to BED format")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output BED file")
    args = parser.parse_args()
    extract_info(args.input, args.output)
