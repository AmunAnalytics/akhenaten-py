# Akhenaten-py

Client to use the plotly hosting service at akhenaten.eu

This library can be used to upload Plotly plots to the akhenaten plotly hosting service!  
To use this service first get an account by contacting frank (at) amunanalytics.eu

If you would like to use a GUI, simply use your client Id and key to login to https://console.akhenaten.eu

## Installation
`python3 -m pip install akhenaten-py`

## Usage
```python
import os

# authentication can be done with environment variables or directly
# this example shows both, this is just to show the possibilities!
os.environ['AKHENATEN_ID'] = '<your client ID>'
os.environ['AKHENATEN_KEY'] = '<your client key'

from akhenaten import AkhenatenClient, MetadataClass
client_hoster = AkhenatenClient(
    # not needed when using environment variables!
    akhenaten_id ='<your client ID>',
    akhenaten_key='<your client key>',
    bucket_name='<bucketname>' # only applicable if you are using custom access key, otherwise deduced from client id
)
# get all current uploaded figs
print(client_hoster.list_figs())

# create some fig
fig = get_some_plotly_fig()
# upload it and display the urls
# if no slug is specified then a random uuid4 will be generated
result = client_hoster.upload_fig(fig, slug='<optional slug>',
  meta_obj = MetadataClass(
            title='some plot title',
            author='some author'
        ))

print(result['json_url']) # the url to use in your own embedding
print(result['fig_url']) # direct html access

# to get back a fig to plotly
fig, meta_obj = client_hoster.download_fig('<slug>')

```

## Alternative usage
This service is backed by minio which is fully AWS S3 compatible.
Thus if you would like more extensive features you can use the ```boto3``` package.  
The hosting url will then be https://s3.akheaten.eu/BUCKET_NAME/ITEM_NAME.json