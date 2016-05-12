#
# pionpion/argparser.py
#

from argparse import ArgumentParser


def standard_parser(*args, **kw):
    """
    Create a 'standard' pionpion argument parser.

    Returns
    -------
        ArgumentParser
            filename : str
                Name of input file
            output_filename : str, optional
                Name of output file
    """
    parser = ArgumentParser(**kw)
    parser.add_argument("filename",
                        help="Filename of root to analyze. "
                             "Multiple files (which will be merged together) "
                             "may be specified with comma separated list.")
    parser.add_argument("--output",
                        nargs='?',
                        default=None,
                        help="Root filename to write results. "
                             "If '-' no output is written")
    return parser
