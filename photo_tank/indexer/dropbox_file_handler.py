__author__ = 'hingem'

import dropbox
import os
from photo_tank.app import app


from photo_tank.model.photo import Photo





def auth_dropbox():

    app_key = 'fhjfjqb8wu3cphh'
    app_secret = '4mry60ezm8pc1e4'

    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print('1. Go to: ' + authorize_url)
    print('2. Click "Allow" (you might have to log in first)')
    print ('3. Copy the authorization code.')
    code = input("Enter the authorization code here: ").strip()

    # This will fail if the user enters an invalid authorization code
    access_token, user_id = flow.finish(code)
    pass

def login(access_token):

    client = dropbox.client.DropboxClient(access_token)
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
    except dropbox.rest.ErrorResponse as e:
        if e.status == 403:
            return True
    except Exception as e:
        return False

def put_photo(photo, client):
    try:
        path = get_paths(photo.files.original_subpath)
        dropbox_path = "{}/{}{}".format(path, photo.id, photo.files.extension)

        if create_path(path, client):

            f = open(photo.files.original_path, 'rb')
            response = client.put_file(dropbox_path,f, overwrite=True)
            photo.dropbox.modified = response["modified"]
            photo.dropbox.revision = response["rev"]
            photo.dropbox.size = response["bytes"]
            photo.dropbox.path = response["path"]
            photo.__mongo_save__()

    except Exception as e:
        return False



    return True

def update_to_dropbox():
    dropbox_client = login(app.config["DROPBOX_ACCESS_TOKEN"])

    cursor = app.db.get_dropbox_updates()
    for rec in cursor:
        photo = Photo(image_id=rec["_id"])
        put_photo(photo, client=dropbox_client)

update_to_dropbox()





