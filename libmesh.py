#!env python3

import requests
import time
import random
import json
import re
import pdb

from utils import my_get_post, print_dict

"""
Классы, обслуживающие Библиотеку МЭШ
"""

class MESHLibrary:

    """ Данные для аутентификации в библиотеке берутся из Дневника """
    def __init__(self, Dnevnik):
        #if not Dnevnik._authenticated:
        #    if not Dnevnik.Authenticate():
        #        raise "Ошибка аутентификации в Электронном дневнике"
        self._auth_token = Dnevnik._auth_token
        self._user_id = Dnevnik._profile['id']
        self._profile_id = Dnevnik._profile['profiles'][0]['id']
        self._ps = Dnevnik._ps


    def Open(self):
        ps = self._ps
        params={ 
            "userId" : self._user_id, 
            "profileId" : self._profile_id,
            "authToken" : self._auth_token}
        r = my_get_post(ps.get, "https://uchebnik.mos.ru/authenticate", params=params)
        opts = {"auth_token" : self._auth_token }
        r = my_get_post(ps.post, "https://uchebnik.mos.ru/api/sessions",
                json=opts, headers={"referer" : r.request.url, "Accept": "application/json; charset=UTF-8"})

    def DownloadComposedDocument(self,id):
        ps = self._ps
        params={}
        r=my_get_post(ps.get, "https://uchebnik.mos.ru/cms/api/composed_documents/"+id, params=params)
        pdb.set_trace()

        pass



