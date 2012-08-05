#!/usr/bin/python
"""
2011.9.23 CKS
A simple utility for uploading images to Picasa.
"""
import os
import dircache
import sys
import time
import datetime

import gdata.photos.service
import gdata.media
import gdata.geo

VERSION = (0, 1, 0)
__version__ = '.'.join(map(str, VERSION))

PRIVATE = 'private' # Anyone with the link can see.
PROTECTED = 'protected' # Only the owner can see.

UPLOAD_DIRECTORY_LOCK = "/tmp/picasa_utils"

def login():
    """
    Programmatically logs into Picasa.
    """
    print 'Logging in...'
    gd_client = gdata.photos.service.PhotosService()
    gd_client.email = os.environ['SMTPUSER'] #type your username here
    gd_client.password = os.environ['SMTPPASS'] # store your password in an environment variable called PASSWD
    gd_client.source = __file__
    gd_client.ProgrammaticLogin()
    print 'Logged in.'
    return gd_client

def get_album_url(gd_client, album):
    """
    Retrieve the album's URL.
    """
    return '/data/feed/api/user/%s/albumid/%s' % (gd_client.email, album.gphoto_id.text)

def get_or_create_album(gd_client, album_name, summary=None, access=PRIVATE):
    """
    Retrieve an existing album or creates one if the album does not yet exist.
    """
    summary = summary or ''
    albums = gd_client.GetUserFeed(user=gd_client.email)
    for album in albums.entry:
        if album.title.text == album_name:
            return album,0
    # Otherwise, album doesn't exist, so create.
    album = gd_client.InsertAlbum(title=album_name, summary=summary, access=access)
    return album,1

def upload(path, album_name,
           default_album_permission=PRIVATE,
           notify_emails=False,
           notify_emails_on_album_creation=False,
           delete_original=False,
           with_prefix=None,
           auto_delete_oldest=False,#TODO
           **kwargs):
    """
    Uploads an image file into a Picasa album.
    """
    print 'Uploading pics from path:',path

    try:
        if os.path.isfile(path):
            DIR_UPLOAD = ''
            pics_list = [path]
        else:
            DIR_UPLOAD = path
            pics_list = dircache.listdir(DIR_UPLOAD)
    except Exception, e:
        print e
        print 'Enter a valid file or directory.'
        usage()

    gd_client = login()
    
    username = gd_client.email#.split('@')[0]
    index = 0

    print 'Retrieving album with username %s...' % (username,)
    #album = gd_client.InsertAlbum(title='New album', summary='This is an album')
    album,album_created = get_or_create_album(gd_client, album_name, access=default_album_permission)#, summary='This is a ')
    album_url = get_album_url(gd_client, album)
    if album_created:
        print 'Album %s created.' % album_url
    else:
        print 'Album %s retrieved.' % album_url
        
    # Ensure album is private.
    album.access.text = default_album_permission
    album = gd_client.Put(album, album.GetEditLink().href, converter=gdata.photos.AlbumEntryFromString)

    print 'Uploading files...'
    count = 0
    for pic in pics_list:
        filename = os.path.join(DIR_UPLOAD, pic)
        while 1:
            try:
                photo = gd_client.InsertPhotoSimple(album_or_uri=album_url,
                                                    title=os.path.split(pic)[-1],
                                                    summary=os.path.split(pic)[-1],
                                                    filename_or_handle=filename,
                                                    content_type='image/jpeg')
                count = count + 1
                print count
                break#TODO:remove
            except Exception, e:
                #TODO:detect error that indicates out-of-space
#                if auto_delete_oldest:
#                    delete_n_oldest_photos(with_prefix=with_prefix)
                msg = 'Count not upload %s. %s' % (filename, str(e))
                print msg
                os.system('email "Error: Unable to upload to Picasa" "%s"' % (msg,))
                break#TODO:remove
    print 'Files uploaded.'
    
    if notify_emails or (notify_emails_on_album_creation and album_created):
        #notify_emails = notify_emails.split(',')
        notify_emails = os.environ['SMTPTOADDRS'].replace(';',',').split(',')
        print "Notifying %s..." % (', '.join(notify_emails),)
        album_url = album.GetHtmlLink().href
        os.system("email \"Picasa Album Update\" \"%s\"" % (album_url,))
        print "Email sent."
        
    if delete_original:
        print 'Deleting original image %s...' % path
        os.remove(path)

def delete_album(album_name):
    """
    Deletes a specific album.
    """
    assert album_name, "An album name must be specified."
    
    gd_client = login()
    
    print 'Deleting album %s...' % (album_name,)
    album,created = get_or_create_album(gd_client, album_name, access=default_album_permission)
    gd_client.Delete(album)
    print 'Album deleted.'

def delete_all_albums(with_prefix=None):
    """
    Deletes all albums.
    """
    
    gd_client = login()
    
    username = gd_client.email
    albums = gd_client.GetUserFeed(user=username)
    for album in albums.entry:
        if with_prefix and not album.title.text.lower().startswith(with_prefix.lower()):
            continue
        print 'Deleting album %s...' % (album.title.text,)
        gd_client.Delete(album)
        print 'Album deleted.'
        
def delete_n_oldest_photos(n=10, **kwargs):
    """
    Deletes the N oldest photos in the oldest album.
    """
    oldest = get_oldest_album(**kwargs)
    if oldest is None:
        return
    dt,album = oldest
    
    def get_pubdate(photo):
        return datetime.datetime(*(time.strptime(photo.published.text.split('.')[0], "%Y-%m-%dT%H:%M:%S")[0:6]))
    
    gd_client = login()
    username = gd_client.email
    photos = gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' % (username, album.gphoto_id.text))
    for i,photo in enumerate(sorted(photos.entry, key=get_pubdate)):
        if i >= n:
            continue
        print 'Deleting %s...' % photo.title.text
        gd_client.Delete(photo)
    
def list_albums():
    """
    Lists all albums.
    """
#    print delete_n_oldest_photos(with_prefix='motion')
#    return
    gd_client = login()
    username = gd_client.email
    albums = gd_client.GetUserFeed(user=username)
    for album in albums.entry:
        print album.title.text
        published_datetime = datetime.datetime(*(time.strptime(album.published.text.split('.')[0], "%Y-%m-%dT%H:%M:%S")[0:6]))
        print '\t',published_datetime
        #print '\t',album.timestamp.text

def get_oldest_album(with_prefix=None):
    """
    Returns the oldest album.
    """
    gd_client = login()
    username = gd_client.email
    albums = gd_client.GetUserFeed(user=username)
    oldest = None
    for album in albums.entry:
        if with_prefix and not album.title.text.lower().startswith(with_prefix.lower()):
            continue
        published_datetime = datetime.datetime(*(time.strptime(album.published.text.split('.')[0], "%Y-%m-%dT%H:%M:%S")[0:6]))
        if oldest is None:
            oldest = (published_datetime, album)
        else:
            oldest = min(oldest, (published_datetime, album))
    return oldest

def upload_directory(directory,
                     album_name,
                     notify_emails_on_album_creation=False,
                     ext='.jpg',
                     auto_delete_oldest=False,
                     with_prefix=None,
                     **kwargs):
    assert os.path.isdir(directory), "'%s' is not a valid directory." % (directory,)
    from lockfile import FileLock, LockTimeout
    try:
        # Acquire lock, so multiple instances of this aren't uploading twice.
        lock = FileLock(UPLOAD_DIRECTORY_LOCK)
        lock_acquired = False
        while not lock.i_am_locking():
            try:
                lock.acquire(timeout=5)
                lock_acquired = True
            except LockTimeout:
                return
        # Post-lock-acquired.
        while 1:
            files = sorted([fn for fn in os.listdir(directory) if fn.endswith(ext)])
            if files:
                for fn in files:
                    upload(path=os.path.join(directory,fn),
                           album_name=album_name,
                           notify_emails_on_album_creation=notify_emails_on_album_creation,
                           auto_delete_oldest=auto_delete_oldest,
                           with_prefix=with_prefix,
                           delete_original=1)
            else:
                # No more files, so exit.
                break
    finally:
        if lock_acquired:
            lock.release()

if __name__=='__main__':
    try:
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option("--album_name", dest="album_name", default='Default',
            help="Name of album to delete or upload an image to.")
        parser.add_option("--filename", dest="filename", default=None,
            help="Name of file to upload.")
        parser.add_option("--delete_album", dest="delete_album", default=None,
            help="If given, the album specified by --album_name will " + \
                "be deleted.")
        parser.add_option("--delete_all_albums", action="store_true",
            default=False,
            help="If given, all albums will be deleted. Use with caution, " + \
                "as this deletes all photos within all the albums, and " + \
                "cannot be undone.")
        parser.add_option("--notify_emails", action="store_true",
            dest="notify_emails", default=False,
            help="If given, the SMTPTOADDRS will be emailed the album URL.")
        parser.add_option("--notify_emails_on_album_creation", 
            action="store_true", dest="notify_emails_on_album_creation",
            default=False,
            help="If given and a new album is created, SMTPTOADDRS will " + \
                "be emailed the album URL.")
        parser.add_option("--delete_original", action="store_true",
            default=False,
            help="If given, original file will be deleted after upload " + \
                "is complete.")
        parser.add_option("--directory", dest="directory", default=None,
            help="Directory to upload files from. Implies --delete_original.")
        parser.add_option("--list_albums", dest="list_albums",
            action="store_true", default=False,
            help="List all albums.")
        parser.add_option("--auto_delete_oldest", dest="auto_delete_oldest",
            action="store_true", default=False,
            help="If given, and a storage error encountered, will delete " + \
                "oldest photos in the oldest album until space is available.")
        parser.add_option("--with_prefix", dest="with_prefix", default=None,
            help="Prefix to use when filtering album names.")
        
        (options, args) = parser.parse_args()
        
        if options.list_albums:
            list_albums()
        elif options.directory:
            upload_directory(**options.__dict__)  
        elif options.filename:
            upload(options.filename, **options.__dict__)
        elif options.delete_album:
            delete_album(options.album_name)
        elif options.delete_all_albums:
            delete_all_albums()
        else:
            parser.print_usage()
    except Exception, e:
        os.system('email "Error: %s" "%s"' % (__file__,str(e)))
        raise