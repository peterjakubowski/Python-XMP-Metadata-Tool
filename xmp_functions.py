# Functions for Python-based XMP Tool
#
# Author: Peter Jakubowski
# Date: 11/18/2023
# Description: Python functions to work with
# XMP metadata using Python XMP Toolkit.
#

# Import necessary packages
from libxmp import XMPFiles, XMPMeta
from libxmp.utils import object_to_dict
import json
import pandas as pd
import os
import glob
from schemas import *


class Asset:
    """
    Structure to store information about image files
    """

    def __init__(self, path):
        self.path = path  # path to image file
        self.filename = self.path.split("/")[-1]  # the file's filename
        self.flickr_id = None  # 10 digit flickr id as string
        self.xmp = None  # xmp metadata packet
        self.xmp_dict = {}  # xmp metadata in a standard Python dictionary
        self.flickr_data = {}  # flickr annotations in a standard Python dictionary
        self.xmp_updates = 0  # number of updates make to xmp packet

    def get_flickr_id(self):
        """
        Extracts the flickr id from the filename
        """

        # split the filename into a list
        id_options = self.filename.strip("_o.jpg").split("_")
        # the flickr id should only contain integer digits, no characters from the alphabet.
        # the number representing the unicode code of a specified character
        # should be between 48-57 to be considered an integer.

        # let's assume the first option we look at is true, until we find otherwise
        found = True
        for d in id_options[-1]:
            if not 48 <= ord(d) <= 57:
                found = False
        # if the first id option meets the requirements, set the flick id to this option
        if found:
            self.flickr_id = id_options[-1]
        # if the first id option does not meet the requirements, let's look at the next
        # option, as long as there is one to look at
        elif len(id_options) > 1:
            # reset found to True
            found = True
            for d in id_options[-2]:
                if not 48 <= ord(d) <= 57:
                    found = False
            # if the second option meets the requirements, set the flickr id to this option
            if found:
                self.flickr_id = id_options[-2]

        return

    def get_xmp_packet(self):
        """
        Opens a file and gets the xmp metadata packet
        """

        # open the file
        xmp_file = XMPFiles(file_path=self.path, open_forupdate=False)
        # get the xmp packet from the file
        xmp = xmp_file.get_xmp()
        # save the xmp packet
        self.xmp = xmp

        return

    def get_xmp_dict(self):
        """
        Extracts all XMP data from a given XMPMeta instance organizing it into a
        standard Python dictionary.
        """

        if self.xmp is not None:
            self.xmp_dict = object_to_dict(self.xmp)

        return

    def replace_xmp_packet(self):
        """
        Replaces the xmp packet in the file with the xmp packet that is
        already open, if such a packet exists.
        """

        if self.xmp is not None and self.xmp_updates > 0:
            # open the file for updating the xmp packet
            xmp_file = XMPFiles(file_path=self.path, open_forupdate=True)
            # check if we can put our xmp packet in the file
            if xmp_file.can_put_xmp(self.xmp):
                # put our xmp packet in the file
                xmp_file.put_xmp(self.xmp)
                # close the file
                xmp_file.close_file()
            else:
                print(f'xmp packet can NOT be put in {self.filename} file!')
        else:
            print(f'No xmp or updates to save to  {self.filename}  file!')

        return

    def retrieve_flickr_json(self, path):
        """
        Opens a json file containing flickr annotations for the corresponding image and
        organizes it into a standard Python dictionary.
        :param path: path to directory where json files are saved
        """

        # check that the path is valid
        if os.path.exists(path):
            if path[-1] != "/":
                path = path + "/"
            # construct the name of the json file
            json_file = path + "photo_" + self.flickr_id + ".json"
            # check that the file exists
            if os.path.exists(json_file):
                # print("loading json file data...")
                j = open(json_file)
                self.flickr_data = json.load(j)

        return

    def merge_flickr_data(self):
        """
        Merges flickr annotations with the file's xmp metadata.
        Uses select fields from provided schema. Uses FLICKR_SCHEMA,
        a dictionary of flickr annotations and xmp metadata mappings
        where the key is the name of the flickr field and the value is a tuple
        with the xmp namespace in the first position, the property name in the
        second position, and the value form of the property
        (simple, unordered, ordered, alternative).
        """

        # iterate over the schema dictionary
        for key, value in FLICKR_SCHEMA.items():
            # unpack the xmp namespace, property, and value form from value tuple
            ns, prop, value_form = value
            # check that the key exists in dictionary
            if key in self.flickr_data:
                # load the flickr data
                fd = self.flickr_data[key]
                # check that the data is not any empty string or list
                if fd != "" and fd != []:
                    # tags are provided in a list of dictionaries in the flickr json,
                    # convert tags to a list of tag values.
                    if key == 'tags':
                        fd = set([d['tag'] for d in fd])
                    # check if the property exists in the xmp metadata
                    if self.xmp.does_property_exist(schema_ns=ns, prop_name=prop):
                        # check if the property is an array
                        if value_form == 'unordered' or value_form == 'ordered':
                            # let's look at the items that are already in the array,
                            # if we find items that are in the flickr data, let's remove
                            # the value from the flickr data, so it is not duplicated in
                            # the xmp metadata.

                            # count the number of items in the array
                            k = self.xmp.count_array_items(schema_ns=ns, array_name=prop)
                            # iterate over the array items:
                            for i in range(k):
                                val = self.xmp.get_array_item(schema_ns=ns, array_prop_name=prop, index=i + 1)
                                # check if the item value is in the flickr data
                                if val in fd:
                                    fd.remove(val)
                            # append the items in flickr data to xmp array
                            for item in fd:
                                # make sure the item is not an empty string
                                if item != "":
                                    self.xmp.append_array_item(schema_ns=ns,
                                                               array_name=prop,
                                                               item_value=item,
                                                               array_options=VALUE_FORMS[value_form])
                                    self.xmp_updates += 1
                        elif value_form == 'alternative':
                            # since we know the property exists, we should consider the current value
                            # and decide whether we want to replace or concatenate values

                            # retrieve the value currently in xmp metadata
                            val = self.xmp.get_localized_text(schema_ns=ns,
                                                              alt_text_name=prop,
                                                              generic_lang='en',
                                                              specific_lang='en-US')
                            # check if the current xmp value is the same as flickr data value
                            if val != fd:
                                # for now, let's replace the xmp value with the flickr data.
                                # set the localized text
                                self.xmp.set_localized_text(schema_ns=ns,
                                                            alt_text_name=prop,
                                                            generic_lang='en',
                                                            specific_lang='x-default',
                                                            prop_value=fd)
                                self.xmp_updates += 1
                        else:
                            # the property is not an array, so we'll treat it as a string.
                            # there is already a string value present in the xmp metadata,
                            # if it's the same value as the flickr data, then we don't need
                            # to do anything. if the values are not the same, we'll need to
                            # decide what to do, replace with the flickr data or concatenate the two.

                            # retrieve the value currently in xmp metadata
                            val = self.xmp.get_property(schema_ns=ns, prop_name=prop)
                            # check if the current xmp value is the same as flickr data value
                            if val != fd:
                                # for now, let's replace the xmp value with the flickr data
                                self.xmp.set_property(schema_ns=ns, prop_name=prop, prop_value=str(fd))
                                self.xmp_updates += 1

                    else:
                        # print(f"{prop} xmp property does not exist")
                        # the xmp property does not exist in the xmp packet, we must create it
                        # if the property is an array, we can append to create the property
                        if value_form == 'unordered' or value_form == 'ordered':
                            # iterate over the items to append in xmp data
                            for item in fd:
                                # make sure the item is not an empty string
                                if item != "":
                                    # append item in xmp array
                                    self.xmp.append_array_item(schema_ns=ns,
                                                               array_name=prop,
                                                               item_value=item,
                                                               array_options=VALUE_FORMS[value_form]
                                                               )
                                    self.xmp_updates += 1
                        elif value_form == 'alternative':
                            # set the localized text
                            self.xmp.set_localized_text(schema_ns=ns,
                                                        alt_text_name=prop,
                                                        generic_lang='en',
                                                        specific_lang='x-default',
                                                        prop_value=fd)
                            self.xmp_updates += 1
                        else:
                            # if the property is not an array, we can set the property value
                            self.xmp.set_property(schema_ns=ns, prop_name=prop, prop_value=fd)
                            self.xmp_updates += 1
            else:
                print(f"FLICKR_SCHEMA key: {key} does not exist in flickr data!")

        return

    def merge_csv_data(self, metadata):
        """
        Merges metadata provided in a csv file with the file's xmp metadata.
        :param metadata: Dictionary, metadata from csv file where keys are the
        XMP namespace and property name formatted like "ns:property"
        """

        # iterate over the items in dictionary
        for key, value in metadata.items():
            # check that the data is not an empty string
            if value != "":
                # split the key into xmp prefix and property values
                key = key.split(":")
                # check that there are two items in key
                if len(key) == 2:
                    # unpack key and assign prefix and property variables
                    prefix, prop = key
                    # check that the xmp prefix and property are included in the schema
                    if prefix in SCHEMA and prop in SCHEMA[prefix]:
                        value_form = SCHEMA[prefix][prop]
                        # get the xmp namespace uri for prefix
                        ns = XMPMeta.get_namespace_for_prefix(prefix)
                        # check if the xmp property exists in asset's xmp packet
                        prop_exists = self.xmp.does_property_exist(schema_ns=ns, prop_name=prop)
                        # check if the property value form is a string
                        if value_form == "simple":
                            # if the xmp property doesn't exist or the values don't match, update the property
                            if (not prop_exists or
                                    self.xmp.get_property(schema_ns=ns, prop_name=prop) != value):
                                # update the value of the property
                                self.xmp.set_property(schema_ns=ns, prop_name=prop, prop_value=value)
                                self.xmp_updates += 1
                        # check if the property value form is an array, check if values need updating
                        elif value_form == "ordered" or value_form == "unordered":
                            # convert the value to a list of values
                            value = [v.strip(" ") for v in value.split(",")]
                            # check if the xmp property exists
                            if prop_exists:
                                # delete the property and create a new array
                                self.xmp.delete_property(schema_ns=ns, prop_name=prop)
                            # iterate over the list of new values and append to array
                            for val in value:
                                self.xmp.append_array_item(schema_ns=ns,
                                                           array_name=prop,
                                                           item_value=val,
                                                           array_options=VALUE_FORMS[value_form])
                                self.xmp_updates += 1
                        # check if the property value form is an alternative array
                        elif value_form == "alternative":
                            # if the xmp property doesn't exist or the values don't match, update the property
                            if (not prop_exists or
                                    self.xmp.get_localized_text(schema_ns=ns,
                                                                alt_text_name=prop,
                                                                generic_lang='en',
                                                                specific_lang='x-default') != value):
                                # set the localized text
                                self.xmp.set_localized_text(schema_ns=ns,
                                                            alt_text_name=prop,
                                                            generic_lang='en',
                                                            specific_lang='x-default',
                                                            prop_value=value)
                                self.xmp_updates += 1
                    else:
                        print((f"XMP property with prefix '{prefix}' "
                               f"and property name '{prop}' is not defined in schema."))
                else:
                    print("key is not valid or formatted incorrectly")

        return

    def retrieve_xmp_metadata(self):
        """
        Retrieves metadata values from xmp packet. Utilizes the SCHEMA dictionary
        of xmp namespaces and property names to extract specific values.
        :return: list of metadata values from properties defined in SCHEMA
        """

        # initialize a list to keep metadata
        metadata = [self.filename]
        # iterate of the items in the schema dictionary
        for prefix, properties in SCHEMA.items():
            # get the xmp namespace uri for prefix
            ns = XMPMeta.get_namespace_for_prefix(prefix)
            # iterate over the properties in properties
            for prop, value_form in properties.items():
                # initialize an empty string to keep the property value
                val = ""
                # check if there is a xmp packet
                if self.xmp is not None:
                    # check if the xmp property exists in the xmp packet
                    if self.xmp.does_property_exist(schema_ns=ns, prop_name=prop):
                        # check if the xmp property is an array
                        if value_form == 'unordered' or value_form == 'ordered':
                            # initialize empty array to store xmp array items
                            arr = []
                            # count the number of items in the array
                            k = self.xmp.count_array_items(schema_ns=ns, array_name=prop)
                            # iterate over the array items:
                            for i in range(k):
                                arr.append(self.xmp.get_array_item(schema_ns=ns, array_prop_name=prop, index=i + 1))
                            # convert the array to a string
                            val = ", ".join(arr)
                        elif value_form == 'alternative':
                            # retrieve the value currently in xmp metadata
                            val = self.xmp.get_localized_text(schema_ns=ns,
                                                              alt_text_name=prop,
                                                              generic_lang='en',
                                                              specific_lang='en-US')
                        else:
                            # the property is a string, append its value to the list
                            val = self.xmp.get_property(schema_ns=ns, prop_name=prop)
                else:
                    print(f"{self.filename} does not contain an xmp packet")
                # append the xmp property value to the list of metadata values
                metadata.append(val)

        return metadata

    def __str__(self):
        # format a string with image attributes
        return f"Filename: {self.filename}\nPath: {self.path}\nFlickr photo id: {self.flickr_id}"


def get_file_paths(path):
    """
    Function takes in a path to a directory or file
    and returns a list of files
    :param path: String, path to directory or file
    :return: list of files
    """

    # keep a list of files
    lst = []
    # first we should check if the path is a valid path
    if os.path.exists(path):
        # let's check if the path is to a directory
        if os.path.isdir(path):
            # print('path is to a directory')
            # get all the paths to jpg images and add them to the list
            for file_path in glob.glob(path + "/*.jpg"):
                lst.append(file_path)
        # let's check if the path is to a file
        elif os.path.isfile(path):
            # print('path is to a file')
            # append file path to the list
            lst.append(path)
        else:
            print('path is not to a directory or a file')
    # if the path is not a valid path, we should let the user know
    else:
        print('the path is not a valid path')

    return lst


def make_file_objects(files):
    """
    Function takes in a list of file paths
    and returns a list of objects of class Asset
    :param files: list of file paths
    :return: list of objects of class Asset
    """

    # keep a list of objects of class Asset
    lst = []
    # iterate over the paths in files
    for path in files:
        # create an object of class Asset and append to list
        lst.append(Asset(path))

    return lst


def load_files(path):
    """
    Wrapper function to load files from a path
    and return a list of objects
    :param path: path to file or directory
    :return: list of objects
    """

    # get a list of files from path
    files = get_file_paths(path)
    # convert the list of file paths to a list of objects
    file_objects = make_file_objects(files)

    return file_objects


def load_csv(path):
    """
    Loads a csv file from a path provided in arguments
    :param path: String, path to csv file
    :return: csv data as a dictionary
    """

    # create an empty dictionary
    df = {}
    # check if the path is valid
    if os.path.exists(path) and os.path.isfile(path):
        # load the csv file using pandas
        df = pd.read_csv(path, index_col=False, dtype=str)
        # set the index to the filename column
        df = df.set_index(keys='filename', drop=True)
        # fill missing values with empty strings
        df = df.fillna("")
        # convert the dataframe to a dictionary
        df = df.to_dict(orient='index')
    else:
        print("path to csv file is not valid!")

    return df


def create_data_frame(data):
    """
    Sets up a new pandas dataframe with retrieved xmp metadata
    and columns named after xmp properties provided in SCHEMA dictionary.
    :param data: retrieved xmp metadata
    :return: empty pandas dataframe with schema property names
    for column names
    """

    # initialize an empty list for column names
    columns = ["filename"]
    # iterate over the lists of property names
    for prefix, properties in SCHEMA.items():
        # concatenate column names with property names
        columns = columns + [prefix + ":" + prop for prop, _ in properties.items()]
    # create pandas dataframe with schema properties as columns
    df = pd.DataFrame(data=data, columns=columns)

    return df
