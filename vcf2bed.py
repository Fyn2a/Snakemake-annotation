import pandas as pd
from fuc import pybed
import argparse

def end_position(value: str):
    if 'END=' in value:
        try:
            end_value = next(part.split('=')[1] for part in value.split(';') if part.startswith('END='))
            return int(end_value) - 1
        except (ValueError, StopIteration):
            return ''
    return ''

def extract_info(cnv_file: str, bed_file: str):
    df = pd.read_csv(cnv_file)
    
    chr = df.iloc[:, 0]
    start = df.iloc[:, 1]
    alt = df.iloc[:, 2].str.replace(r'^<|>$', '', regex=True)
    end = df.iloc[:, 3]
    
    end_pos = end.apply(end_position)    
    
    new_df = pd.DataFrame({
        'chromosome': chr,
        'Start': start,
        'End': end_pos,
        'Type': alt
    })
    new_df.columns = ['Chromosome', 'Start', 'End', 'Type']
    
    bed = pybed.BedFrame.from_frame(data=new_df, meta=[])
    bed.to_file(bed_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CSV to BED format")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output BED file")
    args = parser.parse_args()
    extract_info(args.input, args.output)
