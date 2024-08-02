import gzip
import mimetypes
import brotli
import zlib
import hashlib
import datetime
from pathlib import Path
from typing import Tuple, Dict, Set, Iterable


def extract_meta(meta, cache_file, key, final_row: Dict) -> Tuple[Dict, str, str]:
    final_row = {"cache_file_metadata": {}, "http_response_headers": {}}
    if cache_file is not None:
        cache_file_path = str(cache_file.resolve())
        final_row["cache_file_metadata"]["cache_file"] = cache_file_path
    if key is not None:
        entry, host, uri = key.split()
        final_row["cache_file_metadata"]["key"] = entry
        final_row["cache_file_metadata"]["host"] = host
        final_row["cache_file_metadata"]["uri"] = uri
    if meta is not None:
        final_row["cache_file_metadata"]["request_time"] = meta.request_time
        final_row["cache_file_metadata"]["response_time"] = meta.response_time
        final_row["cache_file_metadata"]["host_address"] = meta.host_address
        final_row["cache_file_metadata"]["host_port"] = meta.host_port

        for attribute, value in meta.http_header_attributes:
            final_row["http_response_headers"][attribute] = value
        out_extension = ""
        if mime := meta.get_attribute("content-type"):
            out_extension = mimetypes.guess_extension(mime[0]) or ""

        content_encoding = (meta.get_attribute("content-encoding") or [""])[0]
        return final_row, out_extension, content_encoding
    else:
        return final_row, "", ""


def extract_data(data: bytes, content_encoding: str, row: Dict, cache_out_dir: Path, out_extension: str) -> Dict:
    if data is not None:
        if content_encoding.strip() == "gzip":
            data = gzip.decompress(data)
        elif content_encoding.strip() == "br":
            data = brotli.decompress(data)
        elif content_encoding.strip() == "deflate":
            data = zlib.decompress(data, -zlib.MAX_WBITS)
        elif content_encoding.strip() != "":
            print(f"Warning: unknown content-encoding: {content_encoding} => {data}")

        h = hashlib.sha256()
        h.update(data)
        cache_file_hash = h.hexdigest()
        file_path = cache_out_dir / (cache_file_hash + out_extension)
        file_link = f'file:///{file_path.resolve()}'
        row["cache_file_metadata"]["file_hash"] = cache_file_hash
        row["cache_file_metadata"]["metadata_link"] = file_link
        with file_path.open("wb") as out:
            out.write(data)
    else:
        row["cache_file_metadata"]["file_hash"] = "<No cache file data>"

    return row


def json_serial(obj):
    """JSON serializer for objects not serializable by default JSON code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    #raise TypeError("Type not serializable")


def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten a nested dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def remove_keys_with_empty_vals(rows: Iterable[Dict]) -> Iterable[Dict]:
    cleaned_rows = [] 
    for row in rows:
        vals = {}
        for key, value in row.items():
            if value:
                if not isinstance(value, str):
                    vals[key] = value
                    continue
                
                c_val = value.replace('\u0000', '')
                if len(c_val) > 0:
                    vals[key] = c_val

        cleaned_rows.append(vals)
    return cleaned_rows

