from chromeCacheExtractor import cacheExtractor
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyzes directory of Chrome cache files")

    # Add arguments
    parser.add_argument('-c', type=str, required=True, help='Path to the Chromium cache directory')
    parser.add_argument('-d', type=str, required=True, help='Path to the output directory')
    parser.add_argument('-o', choices=['json', 'csv'], required=True, help='Output format: json or csv')


    # Parse the arguments
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_arguments()
    c = cacheExtractor(args.c, args.d, args.o)
    c.parse_cache_entries()
