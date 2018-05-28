import logging
import os
import sys

from kiali_qe.utils import get_dict
from kiali_qe.utils.path import conf_path, get_rel_path, log_path

MARKER_LEN = 80


class _RelpathFilter(logging.Filter):
    """Adds the relpath attr to records
    Not actually a filter, this was the least ridiculous way to add custom dynamic
    record attributes and reduce it all down to the ``source`` record attr.
    looks for 'source_file' and 'source_lineno' on the log record, falls back to builtin
    record attributes if they aren't found.
    """
    def filter(self, record):
        record.pathname = get_rel_path(record.pathname)
        # ugly fix to remove python base path for thirdparty library
        _third_party_path = 'site-packages/'
        if _third_party_path in record.pathname:
            record.pathname = record.pathname.split(_third_party_path, 1)[1]
        return True


def format_marker(mstring, mark="-"):
    """ Creates a marker in log files using a string and leader mark.
    This function uses the constant ``MARKER_LEN`` to determine the length of the marker,
    and then centers the message string between padding made up of ``leader_mark`` characters.
    Args:
        mstring: The message string to be placed in the marker.
        leader_mark: The marker character to use for leading and trailing.
    Returns: The formatted marker string.
    Note: If the message string is too long to fit one character of leader/trailer and
        a space, then the message is returned as is.
    """
    if len(mstring) <= MARKER_LEN - 2:
        # Pad with spaces
        mstring = ' {} '.format(mstring)
        # Format centered, surrounded the leader_mark
        format_spec = '{{:{leader_mark}^{marker_len}}}'\
            .format(leader_mark=mark, marker_len=MARKER_LEN)
        mstring = format_spec.format(mstring)
    return mstring


def make_file_handler(cfg):
    if not log_path.exists():
        os.makedirs(log_path.strpath)
    filename = os.path.join(log_path.strpath, cfg.logging.file.filename)
    handler = logging.FileHandler(filename, )
    formatter = logging.Formatter(cfg.logging.file.format)
    handler.setFormatter(formatter)
    handler.setLevel(cfg.logging.file.level)
    return handler


def console_handler(cfg):
    formatter = logging.Formatter(cfg.logging.console.format)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(cfg.logging.console.level)
    handler.setFormatter(formatter)
    return handler


def setup_logger(logger_name, cfg=None):
    # Grab the logging conf
    if cfg is None:
        cfg = get_dict(conf_path.strpath, 'env.yaml')
    logger = logging.getLogger(logger_name)
    # remove all handlers
    logger.handlers = []
    logger.setLevel(logging.DEBUG)
    if cfg.logging.file.enabled:
        logger.addHandler(make_file_handler(cfg))

    if cfg.logging.console.enabled:
        logger.addHandler(console_handler(cfg))

    logger.addFilter(_RelpathFilter())
    return logger


logger = setup_logger('kiali_qe')
