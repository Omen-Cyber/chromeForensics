import argparse
import pathlib
import logging
import csv
import json
from chromeCacheExtractor.cacheExtractor import cacheExtractor as ce
from utils.metaExtractor import remove_keys_with_empty_vals
import datetime


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

    if out_dir.exists():
        raise ValueError("Output directory already exists")

    out_dir.mkdir(parents=True)
    cache_out_dir.mkdir(parents=True)

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
