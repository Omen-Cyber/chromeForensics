from chromeCacheExtractor.CacheExtractor import CacheExtractor as ce
import argparse
import pathlib
import logging


def parse_arguments():

    parser = argparse.ArgumentParser(description="Analyzes directory of Chrome cache files")

    parser.add_argument('-c', type=str, required=True, help='Path to the Chromium cache directory')
    parser.add_argument('-d', type=str, required=True, help='Path to the output directory')
    parser.add_argument('-o', choices=['json', 'csv'], required=True, help='Output format: json or csv')

    return parser.parse_args()

def main(args): 


    # Converting arguments to paths
    in_cache_dir = pathlib.Path(args.c)
    out_dir = pathlib.Path(args.d)
    output_format = pathlib.Path(args.o)
    cache_out_dir = out_dir / "cache_files"

    if not in_cache_dir.is_dir():
        raise ValueError("Input directory is not a directory or does not exist")

    # If output_dir already exists ask user if they want to overwrite
    if out_dir.exists():
        print("Output directory already exists")

    # Creates output directory that contains information about the extracted files including HTTP Response Headers
    # and the directory with the actual cache files
    out_dir.mkdir(exist_ok=True)
    cache_out_dir.mkdir(exist_ok=True)

    # Begin cache extraction process
    extractor = ce(in_cache_dir, out_dir, output_format)
    extractor.parse_cache_entries()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename='chrome_cache_analyzer.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    try:
        cache_args = parse_arguments()
        main(cache_args)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print("ERROR:", e)
        exit(1)

