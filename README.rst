=======================================================================
picasa-utils - Utilities for helping with access to Google's Picasa
=======================================================================

Overview
========

Allows for bulk-uploading of images to Picasa, album creation and deletion.

Installation
------------

Install using pip:

::

    sudo pip install -U https://github.com/chrisspen/picasa-utils/tarball/master

Set the following environment variables in your ~./.bash_aliases or similar startup script:

::

    export SMTPSERVER=smtp.gmail.com
    export SMTPPORT=587
    export SMTPUSER=<username@gmail.com>
    export SMTPPASS="<my super secret password>"
    export SMTPTOADDRS=username_to_be_notified@mydomain.com

The SMTPUSER and SMTPPASS should be the username and password used to access Picasa.

Usage
-----

You can invoke the script either as a Python module or from the command line.

To upload all images in a directory, while deleting the originals and notifying the user via email if a new album was created, run:

::

    picasa_utils.py --delete_original --album_name="My Album $(date +'%%F')" --directory="/tmp/photos"

To permanently delete ALL albums and photos in your Picasa account, which Google provides no easy way to do through the UI, simply run:

::

    picasa_utils.py --delete_all_albums

To see all options, run:

::

    picasa_utils.py --help

References
----------

http://gdata-python-client.googlecode.com/hg/pydocs/gdata.photos.service.html
http://code.google.com/apis/picasaweb/docs/1.0/developers_guide_python.html
http://www.daniweb.com/software-development/python/threads/280403
http://icodesnip.com/snippet/python/flickr-to-picasa-migration-tool
