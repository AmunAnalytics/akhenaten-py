from secret import *
from akhenaten import AkhenatenClient, MetadataClass
import plotly.express as px
import json


if __name__ == '__main__':
    df = px.data.gapminder().query("country=='Canada'")
    fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')

    client = AkhenatenClient()

    r = client.upload_fig(
        fig=fig,
        slug='testplot',
        meta_obj=MetadataClass(
            title='Test Plot',
            author='Tester'
        )
    )

    print(json.dumps(r, indent=4))