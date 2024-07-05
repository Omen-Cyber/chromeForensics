from chromeCacheExtractor import cacheExtractor
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyzes directory of Chrome cache files")

    parser.add_argument('-c', type=str, required=True, help='Path to the Chromium cache directory')
    parser.add_argument('-d', type=str, required=True, help='Path to the output directory')
    parser.add_argument('-o', choices=['json', 'csv'], required=True, help='Output format: json or csv')

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    cache_args = parse_arguments()
    c = cacheExtractor(cache_args.c, cache_args.d, cache_args.o)
    c.parse_cache_entries()

