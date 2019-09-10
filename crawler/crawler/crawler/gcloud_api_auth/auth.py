import os

from google.auth.transport.requests import AuthorizedSession
from google.cloud import storage
from google.cloud.pubsub_v1 import publisher
from google.cloud.pubsub_v1 import subscriber
from google.oauth2 import service_account
from google.cloud import vision

dir_path = os.path.dirname(__file__)


def get_gcloud_pub_client():
    # Explicitly use service account credentials by specifying the private key
    # file.
    pubsub_client = publisher.Client.from_service_account_json(
        dir_path+'/InfluneceForce-bf7751ba4eed.json')
    return pubsub_client


def get_gcloud_sub_client():
    # Explicitly use service account credentials by specifying the private key
    # file.
    pubsub_client = subscriber.Client.from_service_account_json(
        dir_path+'/InfluneceForce-bf7751ba4eed.json')
    return pubsub_client


def get_gcloud_storage_client():
    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json(
        dir_path+'/InfluneceForce-bf7751ba4eed.json')
    return storage_client


def get_gcloud_ImageAnnotatorClient():
    # Explicitly use service account credentials by specifying the private key
    # file.
    credentials = service_account.Credentials.from_service_account_file(
        dir_path + '/InfluneceForce-bf7751ba4eed.json')
    ImageAnnotatorClient =  vision.ImageAnnotatorClient(credentials=credentials)
    return ImageAnnotatorClient


def get_credentials():
    credentials = service_account.Credentials.from_service_account_file(
        dir_path + '/InfluneceForce-bf7751ba4eed.json')
    scoped_credentials = credentials.with_scopes(
        ['https://www.googleapis.com/auth/cloud-platform'])
    print(scoped_credentials)

    authed_session = AuthorizedSession(scoped_credentials)
    # print authed_session.to_string()

    response = authed_session.get(
        'https://www.googleapis.com/storage/v1/b/staging.databeyond-wolverine.appspot.com/o/ring.png')

    media_link = response.json().get('mediaLink')
    print(media_link)

    r = authed_session.get(media_link, stream=True)
    # r = requests.get(media_link, stream=True)

    path = dir_path + '/test.png'

    # image = Image.open(BytesIO(r.content))
    # print (path)
    # image.save(path)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            # print (r.raw.read(10))
            f.write(r.content)
            # shutil.copyfileobj(r.raw, f)
        f.close()

    return r


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = get_gcloud_storage_client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


# if __name__ == "__main__":
#     """
#     For testing
#     """
#     res = get_credentials()
#     files = '/Users/xiaoxizhang/Documents/DataBeyond/pocketX/ring.jpg'
#     dest_file = 'copy3.jpg'
#     upload_blob('staging.databeyond-wolverine.appspot.com', files, dest_file)
#     # hit_probability = 1/50
#     # print(res.text)
#     # print(res.json())
