from minio import Minio
from io import BytesIO
from uuid import uuid4
import os
from minio.error import S3Error
import plotly.io
import plotly.graph_objects as go

from .definitions import MetadataClass

__title__ = "akhenaten-py"
__version__ = "0.2.0"
__author__ = "Frank Boerman"
__license__ = "MIT"


class AkhenatenClient:
    AKHENATEN_URL = "s3.akhenaten.eu"

    def __init__(self, akhenaten_id: str = None, akhenaten_key: str = None, bucket_name: str = None):
        if akhenaten_id is None:
            akhenaten_id = os.getenv('AKHENATEN_ID')
        if akhenaten_key is None:
            akhenaten_key = os.getenv('AKHENATEN_KEY')
        if bucket_name is None:
            self.bucket_name = os.getenv('AKHENATEN_BUCKET')
        else:
            self.bucket_name = bucket_name

        if self.bucket_name is None:
            self.bucket_name = 'b' + akhenaten_id[1:]

        if akhenaten_id is None or akhenaten_key is None or self.bucket_name is None:
            raise Exception("Missing AKHENATEN_ID or AKHENATEN_KEY or AKHENATEN_BUCKET!")

        self.akhenaten = Minio(
            endpoint=self.AKHENATEN_URL,
            access_key=akhenaten_id,
            secret_key=akhenaten_key,
            region="akhenaten"
        )

    def list_figs(self) -> list:
        return [x.object_name.replace('.json', '') for x in self.akhenaten.list_objects(self.bucket_name)
                if x.object_name.endswith('.json')]

    def delete_fig(self, slug: str) -> None:
        fname = slug
        fname_meta = slug
        if not fname.endswith('.json'):
            fname += '.json'
            fname_meta += '.meta.json'

        self.akhenaten.remove_object(
            bucket_name=self.bucket_name,
            object_name=fname
        )
        self.akhenaten.remove_object(
            bucket_name=self.bucket_name,
            object_name=fname_meta
        )

    def upload_fig(self, fig: go.Figure, slug: str = None, meta_obj: MetadataClass = None) -> dict:
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

        r = {
            'slug': slug,
            'json_url': f"https://{self.AKHENATEN_URL}/{self.bucket_name}/{slug}.json",
            'fig_url': f"https://{self.AKHENATEN_URL.replace('s3.', '')}/?bucket={self.bucket_name}&slug={slug}",
            'etag': results.etag
        }

        if meta_obj is not None:
            stream = BytesIO(meta_obj.model_dump_json().encode('utf-8'))
            stream.seek(0)
            results_meta = self.akhenaten.put_object(
                bucket_name=self.bucket_name,
                object_name=f"{slug}.meta.json",
                data=stream,
                length=stream.getbuffer().nbytes,
                content_type='application/json'
            )
            r['meta_json_url'] = f"https://{self.AKHENATEN_URL}/{self.bucket_name}/{slug}.meta.json"
            r['meta_etag'] = results_meta.etag

        return r

    def download_fig(self, slug) -> go.Figure | (MetadataClass | None):
        if slug.endswith('.json'):
            slug = slug.replace('.json', '')

        try:
            r_meta = self.akhenaten.get_object(
                bucket_name=self.bucket_name,
                object_name=slug + '.meta.json'
            )
            meta_obj = MetadataClass(**(r_meta.json()))
        except S3Error:
            meta_obj = None

        try:
            r_fig = self.akhenaten.get_object(
                bucket_name=self.bucket_name,
                object_name=slug + '.json'
            )
            fig = plotly.io.from_json(r_fig.data)
        except S3Error:
            return None

        return fig, meta_obj

