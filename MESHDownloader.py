#!env python3

import json
from pprint import pprint

""" Download composed_material """
def DownloadCM(js):

    print(f"Название: {js['name']}")
    print(f"Описание: {js['description']}")

    print(f"Разделов: {len(js['articles'])}")

    for i in range(len(js['articles'])):
        a=js['articles'][i]
        print(f"{i}. {a['name']}")
        objs=a['layout']['rows'][0]['cells'][0]['content']['objects']
#        print(f": {len(a['layout']['rows'][0]['cells'])}")
        pprint(objs, depth=2)

    pass
