import argparse
import pathlib
import logging
import os
import datetime
import sys
from chromeCacheExtractor.CacheExtractor import CacheExtractor as ce

__description__ = "Extracts cache files and HTTP response headers for Chromium-based browsers that use Simple Cache format"
__organization__ = "Omen-Cyber"
__contact__ = "DaKota LaFeber"
__version__ = 1.0


def parse_arguments():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-c', type=str, required=True, help='Path to the Chromium cache directory (see README.md or common cache for directories)')
    parser.add_argument('-d', type=str, required=True, help='Path to extracted cache files and headers information (cache_report.*)')
    parser.add_argument('-o', choices=['json', 'tsv'], required=True, help='Output format for headers and metadata: json or tsv')
    return parser.parse_args()

def main(args):
    in_cache_dir = pathlib.Path(args.c)
    out_dir = pathlib.Path(args.d)

    if not in_cache_dir.is_dir():
        raise ValueError("Input directory is not a directory or does not exist")

    if out_dir.exists():
        raise ValueError("Output directory already exists")

    logging.info("Analyzing cache files from: " + args.c)
    logging.info("Outputting cache files to: " + args.d)
    logging.info("Output format: " + args.o)

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
        sys.exit(1)
