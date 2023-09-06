from minio import Minio
from pydantic import BaseModel, AnyUrl
from io import BytesIO
from uuid import uuid4
import os
from datetime import datetime

__title__ = "akhenaten-py"
__version__ = "0.1.0"
__author__ = "Frank Boerman"
__license__ = "MIT"


class MetaData(BaseModel):
    author: str = None
    title: str = None
    description: str = None
    avatar: AnyUrl = None
    date: str = None

    def model_post_init(self, __context):
        if self.date is None:
            self.date = datetime.now().strftime("%Y/%m/%d")


class AkhenatenClient:
    AKHENATEN_URL = "s3.akhenaten.eu"

    def __init__(
        self,
        akhenaten_id=None,
        akhenaten_key=None,
        metadata: MetaData = None,
    ):
        if metadata is None:
            metadata = MetaData()
        self.metadata = metadata

        if akhenaten_id is None:
            akhenaten_id = os.getenv("AKHENATEN_ID")
        if akhenaten_key is None:
            akhenaten_key = os.getenv("AKHENATEN_KEY")

        if akhenaten_id is None or akhenaten_key is None:
            raise Exception("Missing AKHENATEN_ID or AKHENATEN_KEY!")

        self.akhenaten = Minio(
            endpoint=self.AKHENATEN_URL,
            access_key=akhenaten_id,
            secret_key=akhenaten_key,
            region="akhenaten",
        )

        self.bucket_name = "b" + akhenaten_id[1:]

    @staticmethod
    def slug_json(slug: str):
        """Returns the slug for the json file"""
        slug.replace(".json", "")
        return f"{slug}.json"

    @staticmethod
    def slug_meta_json(slug: str):
        """Returns the slug for the meta json file"""
        slug.replace(".json", "")
        return f"{slug}.meta.json"

    def list_figs(self):
        return [
            x.object_name.strip(".json")
            for x in self.akhenaten.list_objects(self.bucket_name)
            if x.object_name.endswith(".json")
        ]

    def delete_fig(self, slug):
        slug = self.slug_json(slug)
        self.akhenaten.remove_object(bucket_name=self.bucket_name, object_name=slug)

    def upload_fig(self, fig, slug=None):
        if slug is None:
            slug = str(uuid4())

        stream = BytesIO(fig.to_json().encode("utf-8"))
        stream.seek(0)

        results = self.akhenaten.put_object(
            bucket_name=self.bucket_name,
            object_name=f"{slug}.json",
            data=stream,
            length=stream.getbuffer().nbytes,
            content_type="application/json",
        )
        return {
            "slug": slug,
            "json_url": f"https://{self.AKHENATEN_URL}/{self.bucket_name}/{slug}.json",
            "fig_url": f"https://{self.AKHENATEN_URL.replace('s3.', '')}/{self.bucket_name}/{slug}",
            "etag": results.etag,
        }

    def upload_meta(self, slug):
        """Uploads the meta data for the given slug"""
        slug = self.slug_meta_json(slug)

        stream = BytesIO(self.metadata.model_dump_json().encode("utf-8"))
        stream.seek(0)

        results = self.akhenaten.put_object(
            bucket_name=self.bucket_name,
            object_name=slug,
            data=stream,
            length=stream.getbuffer().nbytes,
            content_type="application/json",
        )
        return {
            "slug": slug,
            "json_url": f"https://{self.AKHENATEN_URL}/{self.bucket_name}/{slug}",
            "etag": results.etag,
        }

    def upload(self, fig, slug=None):
        """Uploads the fig and meta data for the given slug"""
        return self.upload_fig(fig, slug), self.upload_meta(slug)

    def get_fig(self, slug):
        """Returns the json file for the given slug"""
        slug = self.slug_json(slug)

        return self.akhenaten.get_object(
            bucket_name=self.bucket_name, object_name=slug
        ).read()

    def get_meta(self, slug):
        """Returns the json file for the given slug"""
        slug = self.slug_meta_json(slug)

        return self.akhenaten.get_object(
            bucket_name=self.bucket_name, object_name=slug
        ).read()

    def get(self, slug):
        """Returns the fig and meta json file for the given slug"""
        return self.get_fig(slug), self.get_meta(slug)
