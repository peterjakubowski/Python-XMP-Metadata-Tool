# Python-based XMP Tool
#
# Author: Peter Jakubowski
# Date: 11/18/2023
# Description: Python script to read and write
# XMP metadata using Python XMP Toolkit.
#

# Import necessary packages
import sys
import argparse
import xmp_functions
import os.path


def parse_args(args):
    # create an argument parser using argparse
    parser = argparse.ArgumentParser(description="Read and write XMP metadata in image files")
    # add an argument to the parser for the path to the input files
    parser.add_argument("-p", "--path",
                        required=True,
                        help="path to input file or directory",
                        type=str)
    # add an argument to the parser for reading/extracting metadata from images
    parser.add_argument("-r", "--read",
                        help="extract XMP metadata and save to a csv file",
                        action="store_true")
    # add an argument to the parser for writing/embedding metadata in images
    parser.add_argument("-w", "--write",
                        help="embed XMP metadata in file",
                        action="store_true")
    # add a mutually exclusive group to the parser for importing from csv and flickr
    group = parser.add_mutually_exclusive_group()
    # add an argument to the parser for writing/embedding metadata from a csv file in images
    group.add_argument("-i", "--import_csv",
                       help="path to csv file with XMP metadata to import and embed in input file",
                       type=str)
    # add an argument to the parser for writing/embedding flickr metadata from json to xmp
    group.add_argument("-f", "--flickr",
                       help="path to directory with flickr json files, merge flickr annotations with xmp metadata",
                       type=str)
    # parse the arguments in args
    args = parser.parse_args(args)

    return args


def main(args):
    # begin by parsing arguments
    args = parse_args(args)
    # we should create a data structure to keep our files and their attributes tidy,
    # let's get a list of file objects of class Asset
    assets = xmp_functions.load_files(args.path)

    # at this point we should check to make sure we have assets to work with.
    # if our list of assets is empty, there's no reason to continue.
    if len(assets) > 0:
        # initialize an empty dictionary
        csv_metadata = {}
        # check if the --import_csv argument was provided
        if args.import_csv is not None:
            # load the csv file as a dictionary with filenames as keys
            csv_metadata = xmp_functions.load_csv(args.import_csv)
            # print(csv_metadata)

        # no matter the flag provided in our arguments, we'll want to
        # iterate over our list of assets and extract the xmp metadata packet
        # that is embedded in the file

        # let's iterate over our list of assets
        for asset in assets[:]:
            # extract xmp metadata
            asset.get_xmp_packet()
            # convert xmp packet to dictionary
            asset.get_xmp_dict()

            # check if the flickr argument was provided
            if args.flickr is not None:
                # let's parse the asset's filename to get its flickr id,
                # open the asset's corresponding json file containing
                # flickr annotations, and save select data to the asset's
                # xmp packet.

                # get the flickr id
                asset.get_flickr_id()
                # print(asset)
                # if we aren't able to parse a flickr id from the filename, then
                # we don't have a way to open a file's flickr json file, assuming
                # it has one in the first place.
                if asset.flickr_id is not None:
                    # load flickr data
                    asset.retrieve_flickr_json(args.flickr)
                    # if we failed to load the flickr json file, then we won't have
                    # any data to merge with the xmp metadata.
                    if asset.flickr_data != {}:
                        # we should decide what annotations to save/replace in the xmp
                        # id, name (title), description, albums, tags (keywords/subject).
                        # refer to FLICKR_SCHEMA for metadata mappings.

                        # merge flickr annotations with xmp metadata
                        asset.merge_flickr_data()

            # check if metadata was loaded from csv
            elif csv_metadata != {}:
                # check if there is metadata in the dictionary for current asset
                if asset.filename in csv_metadata:
                    # print(csv_metadata[asset.filename])
                    # merge csv data with xmp metadata
                    asset.merge_csv_data(csv_metadata[asset.filename])

            # if the --write flag was provided, we should save
            # the xmp packet back to the file.
            if args.write:
                # check for a xmp packet
                if asset.xmp is not None:
                    # replace the xmp packet in the file with the modified xmp packet
                    print(f"replacing xmp packet in {asset.filename}...")
                    asset.replace_xmp_packet()

        # we're always going to read the embedded xmp metadata, but if we
        # provided the --read flag, we should save a csv file with the
        # xmp metadata. we won't save all the xmp metadata, only the
        # fields/namespaces that we define or provide. Refer to SCHEMA
        # for xmp metadata namespaces and property names.
        if args.read:
            # gather all the metadata in a list
            data = []
            # let's iterate over all the assets and pull out the data that we'd like to save
            for asset in assets[:]:
                # extract xmp metadata values from properties defined in schema and
                # append a list of property values to the list of data
                data.append(asset.retrieve_xmp_metadata())

            # use the data we collected to build a pandas dataframe
            data_frame = xmp_functions.create_data_frame(data)
            # get the path to the directory where we will save the csv file
            directory = "/".join(args.path.split("/")[:-1]) if os.path.isfile(args.path) else args.path
            # make sure the path to the directory ends with a "/"
            if directory[-1] != "/":
                directory = directory + "/"
            # make sure the directory exists before saving the csv file
            if os.path.isdir(directory):
                # save the dataframe to csv
                data_frame.to_csv(directory + 'xmp_metadata.csv', index=False)

    # close the program
    return


if __name__ == '__main__':s
    main(sys.argv[1:])
