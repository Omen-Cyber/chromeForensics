def extract_meta(meta, row: dict, dynamic_row_headers) -> (dict, set, str, str):
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
        # NEED TO RETURN out_extension, content_encoding, row, dynamic_row_headers
        return row, dynamic_row_headers, out_extension, content_encoding
    else:
        return row, dynamic_row_headers, "", ""


def extract_data(data, content_encoding, row, cache_out_dir, out_extension):
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