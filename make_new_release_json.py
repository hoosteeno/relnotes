#!/usr/bin/env python
"""
%prog [-o|--output-dir] [-p|--products] [-c|--channels] [--aurora-suffix] \
    [--beta-suffix] [--esr-suffix]
"""

import copy
import os

from argparse import ArgumentParser

from models.release import Release

# these are the canonical (allowed) values
# TODO: make static functions on these two objects to return this information
PRODUCTS = ['firefox', 'mobile', 'esr']
CHANNELS = ['aurora', 'esr', 'beta', 'release']

# parse cmdline
if __name__ == '__main__':
    parser = ArgumentParser(__doc__)
    parser.set_defaults(
        output_dir='output',
        channels=['aurora', 'beta', 'release'],
        aurora_suffix='a2',
        beta_suffix='beta',
        esr_suffix='',
        products=['firefox', 'mobile']
    )
    parser.add_argument(
        "-o", "--output-dir", dest="output_dir",
        help="specify a location for the generated files to be written to")
    parser.add_argument(
        "-c", "--channels", dest="channels",
        help="comma-separated string of channels to create notes for")
    parser.add_argument(
        "-p", "--products", dest="products",
        help="comma-separated string of products to create notes for")
    parser.add_argument(
        "--aurora-suffix", dest="aurora_suffix",
        help="specify a specific suffix for aurora release")
    parser.add_argument(
        "--beta-suffix", dest="beta_suffix",
        help="specify a specific suffix for beta release")
    parser.add_argument(
        "--esr-suffix", dest="esr_suffix",
        help="specify a specific suffix for esr releases")

    options, args = parser.parse_known_args()

    # channels should be an array
    if (type(options.channels) == str):
        options.channels = [c.strip() for c in options.channels.split(',')]

    # products should be an array
    if (type(options.products) == str):
        options.products = [p.strip() for p in options.products.split(',')]

    # here's where all our data will go
    latest_release = {}

    # we'll do this once for an esr run, and once for all other runs
    def make_json(o):

        # create a latest release for each product specified
        for product in o.products:
            # skip products not in our canonical map
            if product not in PRODUCTS:
                continue

            latest_release[product] = []

            for channel in o.channels:
                # skip channels not in our canonical map
                if channel not in CHANNELS:
                    continue

                # make a release for it
                release = Release(product, channel, o)
                latest_release[product].append(release)

                # output the release to a file/dir
                try:
                    os.makedirs(os.path.join(o.output_dir, release.path))
                except OSError:
                    pass

                full_path = os.path.join(
                    o.output_dir, release.path, release.filename)
                with file(full_path, 'w') as f:
                    f.write(release.json)

                print 'Done: %s' % full_path

    # if esr is in our options, we need to do an esr run
    if 'esr' in options.channels or 'esr' in options.products:
        o = copy.deepcopy(options)
        o.channels = ['esr']
        o.products = ['esr']
        make_json(o)

        # if there are other channels too, we'll run them without esr
        if ('esr' in options.channels):
            options.channels.remove('esr')
        if ('esr' in options.products):
            options.products.remove('esr')

    make_json(options)
