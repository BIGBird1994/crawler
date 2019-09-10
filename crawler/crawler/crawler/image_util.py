from google.cloud import storage
from .gcloud_api_auth.auth import get_gcloud_storage_client
import logging
import os
import urllib.request


def handle_images(img, mid, storage_url, bucket):
    """Download images"""
    logging.info(img)
    tmp_local_path = '/'.join(['/tmp', mid + '-' + img.split('/')[-1]])
    urllib.request.urlretrieve(img, tmp_local_path)
    
    upload_blob(bucket, tmp_local_path, storage_url)
    make_blob_public(bucket, storage_url)
    os.remove(tmp_local_path)


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = get_gcloud_storage_client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(source_file_name)
    
    logging.info('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


def make_blob_public(bucket_name, blob_name):
    """Makes a blob publicly accessible."""
    storage_client = get_gcloud_storage_client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    blob.make_public()
    
    logging.info('Blob {} is publicly accessible at {}'.format(
        blob.name, blob.public_url))
    return blob.public_url
