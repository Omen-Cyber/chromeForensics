import argparse
import pathlib
import logging
import shutil
import os
import csv
import json
from chromeCacheExtractor.cacheExtractor import cacheExtractor as ce
from utils.metaExtractor import remove_keys_with_empty_vals
import datetime

# list of acceptable answers for yes and no
y_list = ["Y", "y", "Yes", "yes", "YES"]
no_list = ["N", "n", "No", "no", "NO"]


def json_serial(obj):
    """JSON serializer for objects not serializable by default JSON code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyzes directory of Chrome cache files")
    parser.add_argument('-c', type=str, required=True, help='Path to the Chromium cache directory')
    parser.add_argument('-d', type=str, required=True, help='Path to the output directory')
    parser.add_argument('-o', choices=['json', 'csv'], required=True, help='Output format: json or csv')
    return parser.parse_args()


def main(args):
    in_cache_dir = pathlib.Path(args.c)
    out_dir = pathlib.Path(args.d)
    cache_out_dir = out_dir / "cache_files"

    if not in_cache_dir.is_dir():
        raise ValueError("Input directory is not a directory or does not exist")
    
    # if output_dir already exists ask user if they want to overwrite
    if out_dir.exists():
        userInput = input("Output directory already exists. Would you like to overwrite? Y/N: ")
        if userInput in y_list:
            for root, dirs, files in os.walk(out_dir):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    shutil.rmtree(os.path.join(root, dir))
        elif userInput in no_list:
            return
        else:
            raise ValueError("Invalid choice: Exiting...")

    out_dir.mkdir(exist_ok=True) # makes dir for json & and csv file
    cache_out_dir.mkdir(exist_ok=True) # makes another dir for storing extracted web pages etc..

    default_row_headers = ["file_hash", "metadata_link", "key", "request_time", "response_time", "date"]
    dynamic_row_headers = set()

    extractor = ce(in_cache_dir, out_dir, cache_out_dir, args.o)
    extractor.parse_cache_entries()
    dynamic_row_headers = extractor.dynamic_row_headers
    rows = extractor.rows

    cleaned_rows = remove_keys_with_empty_vals(rows)

    if args.o == 'csv':
        csv_out_f = (out_dir / "cache_report.csv").open("wt", encoding="utf-8", newline="")
        csv_out_f.write("\ufeff")
        csv_out = csv.DictWriter(
            csv_out_f, fieldnames=default_row_headers + sorted(dynamic_row_headers), dialect=csv.excel,
            quoting=csv.QUOTE_ALL, quotechar="\"", escapechar="\\")
        csv_out.writeheader()
        for row in cleaned_rows:
            csv_out.writerow(row)
        csv_out_f.close()
    elif args.o == 'json':
        json_out_p = out_dir / "cache_report.json"
        with json_out_p.open("w", encoding="utf-8", errors='replace') as json_out_f:
            json.dump(cleaned_rows, json_out_f, ensure_ascii=False, indent=4, default=json_serial)



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename='chrome_cache_analyzer.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    try:
        cache_args = parse_arguments()
        main(cache_args)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print("ERROR:", e)
        exit(1)
