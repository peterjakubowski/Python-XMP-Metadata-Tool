# XMP schemas for Python-based XMP Tool
#
# Author: Peter Jakubowski
# Date: 11/18/2023
# Description: Python dictionaries of schemas to work with
# XMP metadata using Python XMP Toolkit.
#

# This is the schema used when reading (extracting) metadata from files and saving values to a csv output file.
# This same schema is used to import metadata from a csv input file. The csv columns must be in the
# "prefix:property" format and the pairings must be defined in this schema.
# The schema dictionary keys are a xmp prefix and values are dictionaries pairing property names with their value forms.
SCHEMA = {"xmp": {"CreateDate": "simple",
                  "CreatorTool": "simple",
                  "Label": "simple",
                  "Rating": "simple"},
          "photoshop": {"AuthorsPosition": "simple",
                        "Instructions": "simple"},
          "dc": {"creator": "ordered",
                 "subject": "unordered",
                 "description": "alternative",
                 "title": "alternative"},
          "Iptc4xmpExt": {"PersonInImage": "unordered"},
          "tiff": {"ImageWidth": "simple",
                   "ImageLength": "simple",
                   "Make": "simple",
                   "Model": "simple"},
          "exifEX": {"LensModel": "simple"}
          }

# This is the schema used to map flickr annotations to xmp metadata fields.
# The key is the name of the flickr annotation and the values are a tuple describing
# the xmp property the flickr annotation is mapped to. In the first position is
# the xmp namespace (as an uri), the second position is the xmp property name, and the
# third position is the xmp property value form.
FLICKR_SCHEMA = {'id': ('http://ns.adobe.com/photoshop/1.0/', 'Instructions', 'simple'),
                 'name': ('http://purl.org/dc/elements/1.1/', 'title', 'alternative'),
                 'description': ('http://purl.org/dc/elements/1.1/', 'description', 'alternative'),
                 # 'albums': (),
                 'tags': ('http://purl.org/dc/elements/1.1/', 'subject', 'unordered')
                 }

# Dictionary of xmp metadata value forms and their array options.
# xmp properties can be simple (string), an unordered or ordered array, or
# an alternative array.
VALUE_FORMS = {'simple': {},
               'unordered': {'prop_value_is_array': True,
                             'prop_array_is_unordered': True},
               'ordered': {'prop_value_is_array': True,
                           'prop_array_is_ordered': True},
               'alternative': {}
               }
