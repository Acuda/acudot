#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Björn Eistel
# Contact: <eistel@gmail.com>
#
# THIS SOURCE-CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED. IN NO  EVENT WILL THE AUTHOR BE HELD LIABLE FOR
# ANY DAMAGES ARISING FROM THE USE OF THIS SOURCE-CODE.
# USE AT YOUR OWN RISK.

from __future__ import print_function

import sys
import os

import errno

import argparse

def get_files_in_directory(path, stripdir='', data=list()):
    if not len(stripdir):
        stripdir = path

    for entry in os.listdir(path):
        src_filename = os.path.sep.join([path, entry])
        if os.path.isdir(src_filename):
            get_files_in_directory(src_filename, stripdir, data)
        elif os.path.isfile(src_filename):
            dst_filename = src_filename
            if dst_filename.startswith(stripdir):
                dst_filename = dst_filename[len(stripdir):]
            if dst_filename.startswith('/home/USER'):
                dst_filename = dst_filename.replace('/home/USER', os.getenv('HOME'))
            data.append((src_filename, dst_filename))
    return data

def create_symlinks(data, force=False, verbose=False):
    for src, dst in data:
        try:
            os.symlink(src, dst)
        except OSError as ex:
            if not ex.errno is errno.EEXIST:
                raise
            if not force:
                print('File %s exists! Use --force to overwrite. Skipping file' % dst)
                continue

            os.remove(dst)
            os.symlink(src, dst)

        if verbose:
            print('  symlink "%s" created!' % dst)

def is_dotdir(dotdir):
    return not dotdir is None and os.path.isdir(dotdir) and os.access(dotdir, os.R_OK)


def find_dotdir(user_dotdir):
    dot_dir_list = list()

    if is_dotdir(user_dotdir):
        dot_dir_list.append(os.path.realpath(user_dotdir))

    filename = os.path.realpath(__file__) if os.path.islink(__file__) else __file__
    filedir = os.path.dirname(filename)
    dotdir = os.path.sep.join([filedir, 'dotfiles'])
    if 'dotfiles' in os.listdir(filedir) and is_dotdir(dotdir):
        dot_dir_list.append(os.path.realpath(dotdir))

    dotdir = '/opt/acudot/dotfiles'
    if is_dotdir(dotdir):
        dot_dir_list.append(os.path.realpath(dotdir))

    for idx, ddir in enumerate(dot_dir_list):
        print('{: >3}: {}'.format(idx, ddir))

    usr_input = raw_input if sys.version.split('.', 1)[0] == '2' else input

    usr_val = usr_input('Choose DotDir [Default: 0] ')
    try:
        usr_val = 0 if not len(usr_val) else int(usr_val)
    except ValueError:
        print('Input (%r) is not a Number!' % usr_val)
        exit(-1)

    if not 0 <= usr_val < len(dot_dir_list):
        print('Number (%r) not in List' % usr_val)
        exit(-1)

    return dot_dir_list[usr_val]


def main():
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('-f', action="store_true", default=False, dest='force', help="force overwrite if destination exists")
    parser.add_argument('--force', action="store_true", default=False, dest='force', help="force overwrite if destination exists")
    parser.add_argument('--dotdir', default=None, help='dotdir')
    parser.add_argument('-v', action="store_true", default=False, dest='verbose', help="verbose output")
    parser.add_argument('--verbose', action="store_true", default=False, dest='verbose', help="verbose output")
    argparse_result = parser.parse_args(sys.argv[1:])

    dotdir = find_dotdir(argparse_result.dotdir)
    print('Using DotDir:', dotdir)

    data = get_files_in_directory(dotdir)
    create_symlinks(data, force=argparse_result.force, verbose=argparse_result.verbose)

if __name__ == '__main__':
    main()


