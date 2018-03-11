"""Utility and helper functions for MNE-BIDS."""
import os
import errno
from collections import OrderedDict
import json


def _mkdir_p(path):
    """Create a directory, making parent directories as needed.

    From stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def make_bids_filename(subject=None, session=None, task=None,
                       acquisition=None, run=None, processing=None,
                       recording=None, suffix=None, prefix=None):
    """Create a BIDS filename from its component parts.

    BIDS filename prefixes have one or more pieces of metadata in them. They
    must follow a particular order, which is followed by this function. This
    will generate the *prefix* for a BIDS file name that can be used with many
    subsequent files, or you may also give a suffix that will then complete
    the file name.

    Note that all parameters are not applicable to each kind of data. For
    example, electrode location TSV files do not need a task field.

    Parameters
    ----------
    subject : str | None
        The subject ID. Corresponds to "sub".
    session : str | None
        The session for a item. Corresponds to "ses".
    task : str | None
        The task for a item. Corresponds to "task".
    acquisition: str | None
        The acquisition parameters for the item. Corresponds to "acq".
    run : int | None
        The run number for this item. Corresponds to "run".
    processing : str | None
        The processing label for this item. Corresponds to "proc".
    recording : str | None
        The recording name for this item. Corresponds to "recording".
    suffix : str | None
        The suffix of a file that begins with this prefix. E.g., 'audio.wav'.
    prefix : str | None
        The prefix for the filename to be created. E.g., a path to the folder
        in which you wish to create a file with this name.

    Returns
    -------
    filename : str
        The BIDS filename you wish to create.

    Examples
    --------
    >>> print(make_bids_filename(subject='test', session='two', task='mytask', suffix='data.csv')) # noqa
    sub-test_ses-two_task-mytask_data.csv
    """
    order = OrderedDict([('sub', subject),
                         ('ses', session),
                         ('task', task),
                         ('acq', acquisition),
                         ('run', run),
                         ('proc', processing),
                         ('recording', recording)])
    if order['run'] is not None and not isinstance(order['run'], str):
        # Ensure that run is a string
        order['run'] = '{:02}'.format(order['run'])

    _check_types(order.values())

    if not any(isinstance(ii, str) for ii in order.keys()):
        raise ValueError("At least one parameter must be given.")
    filename = []
    for key, val in order.items():
        if val is not None:
            filename.append('%s-%s' % (key, val))
    if isinstance(suffix, str):
        filename.append(suffix)
    filename = '_'.join(filename)
    if isinstance(prefix, str):
        filename = os.path.join(prefix, filename)
    return filename


def make_bids_folders(subject, session=None, kind=None, root=None,
                      make_dir=True):
    """Create a BIDS folder hierarchy.

    This creates a hierarchy of folders *within* a BIDS dataset. You should
    plan to create these folders *inside* the root folder of the dataset.

    Parameters
    ----------
    subject : str
        The subject ID. Corresponds to "sub".
    kind : str
        The kind of folder being created at the end of the hierarchy. E.g.,
        "anat", "func", etc.
    session : str | None
        The session for a item. Corresponds to "ses".
    root : str | None
        The root for the folders to be created. If None, folders will be
        created in the current working directory.
    make_dir : bool
        Whether to actually create the folders specified. If False, only a
        path will be generated but no folders will be created.

    Returns
    -------
    path : str
        The (relative) path to the folder that was created.

    Examples
    --------
    >>> print(make_bids_folders('sub_01', session='my_session',
                                kind='meg', root='path/to/project', make_dir=False))  # noqa
    path/to/project/sub-sub_01/ses-my_session/meg
    """
    _check_types((subject, kind, session, root))

    path = ['sub-%s' % subject]
    if isinstance(session, str):
        path.append('ses-%s' % session)
    if isinstance(kind, str):
        path.append(kind)
    path = os.path.join(*path)
    if isinstance(root, str):
        path = os.path.join(root, path)

    if make_dir is True:
        _mkdir_p(path)
    return path


def make_dataset_description(path, name=None, bids_version=None, license=None,
                             authors=None, acknowledgements=None,
                             how_to_acknowledge=None, funding=None,
                             references_and_links=None, doi=None,
                             verbose=False):
    """Create json for a dataset description.

    BIDS datasets may have one or more fields, this function allows you to
    specify which you wish to include in the description. See the BIDS
    documentation for information about what each field means.

    Parameters
    ----------
    path : str
        A path to a folder where the description will be created.
    name : str | None
        The name of this BIDS dataset.
    bids_version : str | None
        The version of the BIDS specification to which this dataset adheres.
    license : str | None
        The license under which this datset is published.
    authors : str | None
        Authors who contributed to this dataset.
    acknowledgements : str | None
        Acknowledgements for this dataset.
    how_to_acknowledge : str | None
        Instructions for how acknowledgements/credit should be given for this
        dataset.
    funding : str | None
        Funding sources for this dataset.
    references_and_links : str | None
        References or links for this dataset.
    doi : str | None
        The DOI for the dataset.
    """
    fname = os.path.join(path, 'dataset_description.json')
    description = OrderedDict([('Name', name),
                               ('BIDSVersion', bids_version),
                               ('License', license),
                               ('Authors', authors),
                               ('Acknowledgements', acknowledgements),
                               ('HowToAcknowledge', how_to_acknowledge),
                               ('Funding', funding),
                               ('ReferencesAndLinks', references_and_links),
                               ('DatasetDOI', doi)])

    _write_json(description, fname, verbose=verbose)


def _check_types(variables):
    """Make sure all variables are strings or None."""
    types = set(type(ii) for ii in variables)
    for itype in types:
        if not isinstance(itype, type(str)) and itype is not None:
            raise ValueError("All values must be either None or strings. "
                             "Found type %s." % itype)


def _write_json(dictionary, fname, verbose=False):
    """Write JSON to a file."""
    json_output = json.dumps(dictionary, indent=4)
    with open(fname, 'w') as fid:
        fid.write(json_output)
        fid.write('\n')

    if verbose is True:
        print(os.linesep + "Writing '%s'..." % fname + os.linesep)
        print(json_output)
