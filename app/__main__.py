# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import json
import os.path
import zipfile
# from pprint import pprint as pp

# from modules import module_name


def load_zipped_config(json_config_file_name):
    zipfile_path = os.path.dirname(os.path.realpath(__file__))
    with zipfile.ZipFile(zipfile_path, 'r') as this_zip:
        return json.loads(this_zip.read(json_config_file_name))


def load_prezipped_config(json_config_file_name):
    config_path = os.path.join(os.path.dirname(__file__),
                               json_config_file_name)
    with open(config_path) as json_config:
        return json.load(json_config)


def main():
    pass


if __name__ == '__main__':
    main()