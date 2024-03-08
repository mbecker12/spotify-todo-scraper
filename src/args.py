import argparse
import logging

def parse_args():
    def set_logging_level(loglevel: str):
        numeric_level = getattr(logging, loglevel.upper(), None)
        logging.getLogger().setLevel(numeric_level)
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--danger-run",
        help="Omit the default dry-run setting and delete tracks from playlist.",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--loglevel",
        default="INFO",
        help="controls verbosity - DEBUG/INFO/WARNING/ERROR/CRITICAL",
    )
    args = parser.parse_args()
    set_logging_level(args.loglevel)
    return args
