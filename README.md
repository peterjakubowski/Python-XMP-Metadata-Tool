# Python-XMP-Metadata-Tool

This is a Python program that reads and writes XMP metadata using Python XMP Toolkit. The program accomplishes several tasks:

1) Reads XMP metadata from images (files) and saves values to a csv file.
2) Reads a csv file with metadata values and writes XMP metadata to images (files).
3) Merges data from Flickr json files with XMP metadata in images (files).

One of the primary purposes of this program is to facilitate data migration from the Flickr photo platform to a digital asset management system. One strategy for migrating metadata is to embed all XMP metadata in the images for the new DAM to extract. When exporting original images from Flickr, any metadata that was modified after upload to the platform will not be embedded in the exported images, but will be provided in JSON files. This Python program scans a directory of original Flickr images and merges annotations from the JSON files with XMP metadata in the original images.

## What is XMP metadata?

## Usage

```
usage: xmp_tool.py [-h] -p PATH [-r] [-w] [-i IMPORT_CSV | -f FLICKR]

Read and write XMP metadata in image files

optional arguments:
  -h, --help                show this help message and exit
  -p PATH, --path PATH      path to input file or directory
  -r, --read                extract XMP metadata and save to a csv file
  -w, --write               embed XMP metadata in file
  -i IMPORT_CSV,
  --import_csv IMPORT_CSV   path to csv file with XMP metadata to import
                            and embed in input file
  -f FLICKR,
  --flickr FLICKR           path to directory with flickr json files,
                            merge flickr annotations with xmp metadata
```

Provide a path to a single image or a directory of many images. Use the -r flag to extract XMP metadata from the input files and save a csv file with metadata values.
```
python xmp_tool.py -p path/to/images/ -r
```

Use the -i flag and provide a path to a csv file to import XMP metadata. Use the -w flag to write any changes to the metadata in the file.

```
python xmp_tool.py -p path/to/images/ -i path/to/csv/metadata.csv -w
```

Use the -f flag and provide a path to a directory with json files from Flickr to import XMP metadata. Use the -w flag to write any changes to the metadata in the file.
```
python xmp_tool.py -p path/to/images/ -f path/to/directory/json/files/ -w
```

## Files
 
* `xmp_tool.py` - Contains the main python script.
* `xmp_functions.py` - Class and Functions for xmp_tool.py that perform various steps of the process.
* `schemas.py` - Contains dictionaries of schemas to work with XMP metadata

## Dependencies
```
Python 3.9
pandas 1.5.3
python-xmp-toolkit 2.0.1
Exempi 2.2.0+
```
