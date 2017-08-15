#!env python3

import calendar
import requests
import time
import random
import json

from utils import my_get_post



"""
Class to access to E-Diary
"""

class Dnevnik:
    """ Class to access electronic diary """
    def __init__(self, pgu_auth):
        """ pgu_auth: authenticator class for PGU """
        self._auth=pgu_auth
        self._data_url="https://my.mos.ru/data/"
        self._authenticated=False
        

    def Authenticate(self):
        """ authentication to PGU """
        if not self._auth.Authenticated:
            self._auth.Authenticate()

        self._ps=self._auth._ps

        milisecs=calendar.timegm(time.gmtime())*1000+random.randint(0,999)+1
        r=my_get_post(self._ps.get, "https://my.mos.ru/static/xdm/index.html?nocache="+str(milisecs)+"&xdm_e=https%3A%2F%2Fwww.mos.ru&xdm_c=default1&xdm_p=1")
        self._ps.cookies.update(r.cookies)
        r=my_get_post(self._ps.get,r.headers['Location'])
        self._ps.cookies.update(r.cookies)
        r=my_get_post(self._ps.get,r.headers['Location'])
        self._ps.cookies.update(r.cookies)
        r=my_get_post(self._ps.get,r.headers['Location'])
       
    #    ps.cookies.update(r.cookies)
    #    print_dict(ps.cookies)
        #ref="https://my.mos.ru/static/xdm/index.html?nocache="+str(milisecs)+"&xdm_e=https%3A%2F%2Fwww.mos.ru&xdm_c=default1&xdm_p=1"

        #r=my_get_post(ps.get,"https://my.mos.ru/static/js/easyXDM-2.4.17.1.min.js", headers={"referer" :    ref })
        #r=my_get_post(ps.get,"https://my.mos.ru/static/js/xdm.min.js", headers={"referer" :    ref })
        
        r=my_get_post(self._ps.get,"https://www.mos.ru/api/oauth20/v1/frontend/json/ru/options")
        opts=json.loads(r.text)

        # надо: nonce signature timestamp
        #print("token request cookies:")
        #print_dict(ps.cookies)
        token_data={"signature":opts["elk"]["signature"],"nonce":opts["elk"]["nonce"],
                "timestamp":opts["elk"]["timestamp"],"system_id":opts["elk"]["system_id"]}
        r=my_get_post(self._ps.post,self._data_url+"token", data=token_data)

        self._diary_token=json.loads(r.text)["token"]

        print("E_DIARY token:"+self._diary_token)

        pass

    def ListDiaryAccounts(self):
        """ Get list of diary accounts """
        milisecs=calendar.timegm(time.gmtime())*1000+random.randint(0,999)+1
        r=my_get_post(self._ps.get,self._data_url+self._diary_token+"/profile/me/E_DIARY/?_="+str(milisecs))
        j=json.loads(r.text)
        r=[]
        for d in j["data"]:
            system=""
            try:
                system=d["SYSTEM"]
            except:
                pass
            a=DiaryAccount(d["LOGIN"],d["COMMENT"],d["PASSWORD"], system)
            
            r.append( a)


        return r
        pass

    def SelectDiaryAccount(id):
        """ Select diary account """
        pass

    def ListStudents():
        """ Get list of supervised students """
        pass

    def SelectStudent(id):
        """ Select student """
        pass


class DiaryAccount:
    """ """
    def __init__(self, login, comment, password, system):
        self.login=login
        self.comment=comment
        self.password=password
        self.system=system

    def __repr__(self):
        return "r[%s] : login=%s password=%s\n" %(self.comment, self.login, self.password)
        
    def __str__(self):
        return "s[%s] : login=%s password=%s\n" %(self.comment, self.login, self.password)



