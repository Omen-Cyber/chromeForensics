def guess_cache_class(
        cache_dir: Optional[Union[pathlib.Path, os.PathLike]]) -> Optional[str]:
    cache_dir = pathlib.Path(cache_dir)
    data_files = {"data_0", "data_1", "data_2", "data_3"}

    for file in cache_dir.iterdir():
        if file.name == "index-dir":
            return "ChromiumSimpleFileCache"
        elif file.name in data_files:
            return "ChromiumBlockFileCache"
        elif re.match(r"f_[0-9a-f]{6}", file.name):
            return "ChromiumBlockFileCache"
        elif re.match(r"^[0-9a-f]{16}_0$", file.name):
            return "ChromiumSimpleFileCache"

    return None