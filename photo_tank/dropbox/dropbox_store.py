__author__ = 'hingem'
# Include the Dropbox SDK
import dropbox

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

def put_photo(photo):
    access_token = 'UFefx_vmXWwAAAAAAAAK7WmXaQf6_uYnZQpJrP9bZ7uGWIaAdLQw8tiU4wYyBd1F'
    user_id = '8285415'
    client = dropbox.client.DropboxClient(access_token)
    print('linked account: ', client.account_info())

    f = open('working-draft.txt', 'rb')
    response = client.put_file('/magnum-opus.txt', f)
    print('uploaded: ', response)

    folder_metadata = client.metadata('/')
    print('metadata: ', folder_metadata)

    f, metadata = client.get_file_and_metadata('/magnum-opus.txt')
    out = open('magnum-opus.txt', 'wb')
    out.write(f.read())
    out.close()
    print(metadata)

put_photo()