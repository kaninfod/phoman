__author__ = 'hingem'

from dropbox.client import DropboxClient, DropboxOAuth2FlowNoRedirect
from dropbox.rest import ErrorResponse, RESTSocketError
import os
from photo_tank.app import app

from photo_tank.model.photo import Photo

def auth_dropbox():

    app_key = 'fhjfjqb8wu3cphh'
    app_secret = '4mry60ezm8pc1e4'

    flow = DropboxOAuth2FlowNoRedirect(app_key, app_secret)

    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print('1. Go to: ' + authorize_url)
    print('2. Click "Allow" (you might have to log in first)')
    print ('3. Copy the authorization code.')
    code = input("Enter the authorization code here: ").strip()

    # This will fail if the user enters an invalid authorization code
    access_token, user_id = flow.finish(code)


def login(access_token):

    client = DropboxClient(access_token)
    return client

def get_paths(photo_path):

    p, day = os.path.split(photo_path)
    p, month = os.path.split(p)
    p, year = os.path.split(p)


    path = "/{}/{}/{}".format(year ,month, day)

    return path
def create_path(path, client):
    try:
        response = client.file_create_folder(path=path)
        return True
    except ErrorResponse as e:
        if e.status == 403:
            return True
    except Exception as e:
        return False

def check_file_exist(client, path, photo):
    response = client.metadata(path)
    if photo.dropbox.revision == response["rev"] and photo.dropbox.size:
        return True
    else:
        return False



def put_photo(photo, client):
    try:
        path = get_paths(photo.files.original_subpath)
        dropbox_path = "{}/{}{}".format(path, photo.id, photo.files.extension)
        if not check_file_exist(client, dropbox_path, photo):
            if create_path(path, client):
                f = open(photo.files.original_path, 'rb')
                response = client.put_file(dropbox_path,f, overwrite=True)
                photo.dropbox.modified = response["modified"]
                photo.dropbox.revision = response["rev"]
                photo.dropbox.size = response["bytes"]
                photo.dropbox.path = response["path"]
                photo.save()

    except Exception as e:
        return False

    return True

def dropbox_watcher():
    dropbox_client = login(app.config["DROPBOX_ACCESS_TOKEN"])

    cursor = app.db.get_dropbox_updates()
    for rec in cursor:
        photo = Photo(image_id=rec["_id"])
        put_photo(photo, client=dropbox_client)







