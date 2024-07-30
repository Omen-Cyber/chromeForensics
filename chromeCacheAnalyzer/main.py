import argparse
import pathlib
import logging
import shutil
import os
import datetime

from chromeCacheExtractor.CacheExtractor import CacheExtractor as ce


def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyzes directory of Chrome cache files")
    parser.add_argument('-c', type=str, required=True, help='Path to the Chromium cache directory')
    parser.add_argument('-d', type=str, required=True, help='Path to the output directory')
    parser.add_argument('-o', choices=['json', 'csv'], required=True, help='Output format: json or csv')
    return parser.parse_args()

def main(args):
    in_cache_dir = pathlib.Path(args.c)
    out_dir = pathlib.Path(args.d)

    if not in_cache_dir.is_dir():
        raise ValueError("Input directory is not a directory or does not exist")

    if out_dir.exists():
        raise ValueError("Output directory already exists")

    extractor = ce(in_cache_dir, out_dir, args.o)
    extractor.parse_simple_cache_entries()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename='chrome_cache_analyzer.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    try:
        cache_args = parse_arguments()
        main(cache_args)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print("ERROR:", e)
        exit(1)
