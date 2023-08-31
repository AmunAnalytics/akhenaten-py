from minio import Minio
from io import BytesIO
from uuid import uuid4
import os

__title__ = "akhenaten-py"
__version__ = "0.1.0"
__author__ = "Frank Boerman"
__license__ = "MIT"


class AkhenatenClient:
    AKHENATEN_URL = "s3.akhenaten.eu"

    def __init__(self, akhenaten_id=None, akhenaten_key=None):
        if akhenaten_id is None:
            akhenaten_id = os.getenv('AKHENATEN_ID')
        if akhenaten_key is None:
            akhenaten_key = os.getenv('AKHENATEN_KEY')

        if akhenaten_id is None or akhenaten_key is None:
            raise Exception("Missing AKHENATEN_ID or AKHENATEN_KEY!")

        self.akhenaten = Minio(
            endpoint=self.AKHENATEN_URL,
            access_key=akhenaten_id,
            secret_key=akhenaten_key,
            region="akhenaten"
        )

        self.bucket_name = 'b' + akhenaten_id[1:]

    def list_figs(self):
        return [x.object_name.strip('.json') for x in self.akhenaten.list_objects(self.bucket_name)
                if x.object_name.endswith('.json')]

    def delete_fig(self, slug):
        if not slug.endswith('.json'):
            slug += '.json'
        self.akhenaten.remove_object(
            bucket_name=self.bucket_name,
            object_name=slug
        )

    def upload_fig(self, fig, slug=None):
        if slug is None:
            slug = str(uuid4())

        stream = BytesIO(fig.to_json().encode('utf-8'))
        stream.seek(0)

        results = self.akhenaten.put_object(
            bucket_name=self.bucket_name,
            object_name=f"{slug}.json",
            data=stream,
            length=stream.getbuffer().nbytes,
            content_type='application/json'
        )
        return {
            'slug': slug,
            'json_url': f"https://{self.AKHENATEN_URL}/{self.bucket_name}/{slug}.json",
            'fig_url': f"https://{self.AKHENATEN_URL.replace('s3.', '')}/{self.bucket_name}/{slug}",
            'etag': results.etag
        }