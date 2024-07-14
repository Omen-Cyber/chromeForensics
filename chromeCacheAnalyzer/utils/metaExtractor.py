import gzip
import mimetypes
import brotli
import zlib
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Set, Iterable


def extract_meta(meta, row: Dict, dynamic_row_headers: Set) -> Tuple[Dict, Set, str, str]:
    if meta is not None:
        row["request_time"] = meta.request_time
        row["response_time"] = meta.response_time
        for attribute, value in meta.http_header_attributes:
            dynamic_row_headers.add(attribute)
            if attribute in row:
                row[attribute] += f"; {value}"
            else:
                row[attribute] = value
        
        out_extension = ""
        if mime := meta.get_attribute("content-type"):
            out_extension = mimetypes.guess_extension(mime[0]) or ""

        content_encoding = (meta.get_attribute("content-encoding") or [""])[0]
        return row, dynamic_row_headers, out_extension, content_encoding
    else:
        return row, dynamic_row_headers, "", ""


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
        row["file_hash"] = cache_file_hash
        row["metadata_link"] = file_link
        with file_path.open("wb") as out:
            out.write(data)
    else:
        row["file_hash"] = "<No cache file data>"

    return row


def has_non_empty_values(row: Dict, dynamic_headers: Set) -> bool:
    for header in dynamic_headers:
        if row.get(header) not in (None, ""):
            return True
    return False


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

