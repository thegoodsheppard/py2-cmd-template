#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import zipfile
import os.path
import os
import shutil
from pprint import pprint as pp
import json

underline = '\x1b[4m'
clear = '\x1b[0m'


def get_dirpath(file):
    return os.path.dirname(os.path.realpath(file))


def get_sib_dir(dir=None, sibname=None):
    parent_dir = os.path.dirname(dir)
    sib_dir = os.path.join(parent_dir, sibname)
    if not os.path.isdir(sib_dir):
        raise ValueError('\n{} does not exist'.format(sib_dir))
    else:
        return sib_dir


def get_app_packages(app_root):
    return [
        dirpath for dirpath, _, files in os.walk(app_root)
        if '__init__.py' in files
    ]


def get_paths():
    try:
        build_dir = get_dirpath(__file__)
        output_dir = os.path.join(build_dir, 'output')
        app_dir = get_sib_dir(dir=build_dir, sibname='app')
        project_root = get_dirpath(build_dir)
        app_name = os.path.basename(project_root)
        output_pyzip_path = os.path.join(output_dir,
                                         '{}.command'.format(app_name))
        input_pyapp_package_paths = get_app_packages(app_dir)
        zipwrap_path = os.path.join(output_dir, '{}.zip'.format(app_name))
        return (app_dir, output_dir, output_pyzip_path,
                input_pyapp_package_paths, zipwrap_path)
    except StandardError as error:
        pp(error)
        print('\nError getting required file paths\n')
        exit(1)


def create_zip_with_header(output_pyzip_path, file_header_lines):
    try:
        with open(output_pyzip_path, 'a') as this_zip:
            this_zip.writelines(file_header_lines)
    except StandardError as error:
        pp(error)
        print('\nError creating file\n')
        exit(1)


def append_pyzip_root(output_pyzip_path, config_path, config_file_name):
    try:
        with zipfile.ZipFile(output_pyzip_path, 'a') as this_zip:
            this_zip.write(config_path, config_file_name)
    except StandardError as error:
        pp(error)
        print('\nError appending {} file\n'.format(config_file_name))
        exit(1)


def append_pyzip_packages(output_pyzip_path, app_dir,
                          input_pyapp_package_paths):
    try:
        with zipfile.PyZipFile(output_pyzip_path, 'a') as this_zip:
            this_zip.writepy(app_dir)
            for package in input_pyapp_package_paths:
                this_zip.writepy(package)
    except StandardError as error:
        pp(error)
        print('\nError appending zip data to file\n')
        exit(1)


def set_read_exec(output_pyzip_path):
    try:
        os.chmod(output_pyzip_path, 0555)
    except StandardError as error:
        pp(error)
        print('\nError changing file permissions\n')
        exit(1)


def zip_wrap(inner_zip, outer_zip):
    with zipfile.ZipFile(outer_zip, 'w') as this_zip:
        this_zip.write(inner_zip, os.path.basename(inner_zip))
    os.remove(inner_zip)


def delete_previous_output(output_dir):
    try:
        shutil.rmtree(output_dir)
    except OSError as os_error:
        if os_error[0] != 2:  # 'No such file or directory'
            print('Error deleting {}:'.format(output_dir))
            pp(os_error)
            exit(1)
    except StandardError as error:
        print('Error deleting {}:'.format(output_dir))
        pp(error)
        exit(1)
    try:
        os.mkdir(output_dir)
    except StandardError as error:
        print('Error creating {}:'.format(output_dir))
        pp(error)
        exit(1)


def get_filename_id(app_dir, json_config_file_name):
    json_config_file = os.path.join(app_dir, json_config_file_name)
    try:
        with open(json_config_file) as config:
            return json.load(config)['filename_id']
    except StandardError:
        print('Error reading customer name not from config')


def main():

    # must add newlines
    file_header_lines = [
        '#!/usr/bin/python\n\n',
        '# Please contact greg.sheppard@zones.com with any questions\n\n'
    ]

    config_file_name = '.config.json'

    (app_dir, output_dir, output_pyzip_path, input_pyapp_package_paths,
     zipwrap_path) = get_paths()

    delete_previous_output(output_dir)

    filename_id = get_filename_id(app_dir, config_file_name)

    config_path = os.path.join(app_dir, config_file_name)

    renamed_pyzip = output_pyzip_path.replace(
        '.command', '_{}.command'.format(filename_id))
    create_zip_with_header(renamed_pyzip, file_header_lines)

    append_pyzip_root(renamed_pyzip, config_path, config_file_name)

    # watch out for extraneous __init__.py files
    # maybe just do one os.walk for both the root and the packages/modules
    append_pyzip_packages(renamed_pyzip, app_dir, input_pyapp_package_paths)

    set_read_exec(renamed_pyzip)

    renamed_zipwrap_path = zipwrap_path.replace('.zip',
                                                '_{}.zip'.format(filename_id))
    zip_wrap(renamed_pyzip, renamed_zipwrap_path)

    print("Build succeeded; file written to '{}{}{}'".format(
        underline, renamed_zipwrap_path, clear))


if __name__ == '__main__':
    main()
