from chromeCacheAnalyzer.chromeCacheExtractor.cacheExtractor import cacheExtractor as ce
import argparse
import pathlib

def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyzes directory of Chrome cache files")

    parser.add_argument('-c', type=str, required=True, help='Path to the Chromium cache directory')
    parser.add_argument('-d', type=str, required=True, help='Path to the output directory')
    parser.add_argument('-o', choices=['json', 'csv'], required=True, help='Output format: json or csv')

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    try:
        cache_args = parse_arguments()
        if not pathlib.Path(cache_args.c).exists():
            print("ERROR: Cache directory does not exist")
            raise FileNotFoundError
        if "~" in str(pathlib.Path(cache_args.d)):
            cache_args.d = str(pathlib.Path(cache_args.d).expanduser())
    except Exception as e:
        print("ERROR: ", e)
        exit(1)
    c = ce(cache_args.c, cache_args.d, cache_args.o)
    c.parse_cache_entries()

