# Chrome Cache Forensics Tool

## Overview

The Chrome Cache Forensics Tool is designed for digital forensic analysts and cybersecurity professionals to parse and analyze Google Chrome's cache files. This tool extracts metadata and cached content from both the Block File Cache and Simple File Cache formats used by Chrome.

## Features

- **Cache Parsing**: Supports parsing of both Block File Cache and Simple File Cache formats.
- **Metadata Extraction**: Extracts detailed metadata from cache entries, including request and response times, headers, and more.
- **Data Export**: Exports extracted data to TSV and JSON formats for easy analysis and reporting.
- **Logging**: Comprehensive logging for audit trails and debugging.
- **Modular Design**: Well-structured codebase with clear separation of responsibilities for easy maintenance and extension.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Omen-Cyber/chromeForensics.git
   cd chromeCacheAnalyzer
   ```

 2. Install the required dependencies:
  ```bash
   pip install -r requirements.txt 
   ```

## Usage

### Command Line

Use this command to run the tool:
```shell
python3 main.py -c <cache_input_dir> -d <output_dir> -o <output_format>
```
- **<cache input dir>**: Path to the directory containing Chrome's cache files.
- **<output dir>**: Path to the directory where the output files will be saved.
- **<output format>**: The format for the extracted data. (json or tsv)

### Output

The tool will generate:

- A TSV file (`cache_report.tsv`) containing a structured view of the extracted metadata.
- A JSON file (`cache_report.json`) containing the same data in JSON format.
- A directory (`cache_files`) containing extracted cache files, images, and HTML pages.
- A log file (`chrome_cache_analyzer.log`) containing informational and error log messages.


## Chrome Cache Locations

- **Windows 10/11**: C:\Users\Username\AppData\Local\Google\Chrome\User Data\Default\Cache
- **Linux**: /home/<username>/.cache/google-chrome/Default/Cache/Cache_Data
- **Mac**: /Users/<username>/Library/Caches/Google/Chrome/Default/Cache


## Contact

DaKota LaFeber - linkedin: dakota-lafeber2 - df@omencyber.io

Project Link: https://github.com/Omen-Cyber/chromeForensics
