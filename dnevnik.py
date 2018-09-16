#!env python3

import calendar
import requests
import time
import random
import json
import re
import pdb


from utils import my_get_post, print_dict



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
        ps=self._ps
        #pdb.set_trace()
        ps.cookies["mos_id"]="CllGxlmW7RAJKzw/DJfJAgA="

        milisecs=calendar.timegm(time.gmtime())*1000+random.randint(0,999)+1
        r=my_get_post(ps.get, "https://my.mos.ru/static/xdm/index.html?nocache="+str(milisecs)+"&xdm_e=https%3A%2F%2Fwww.mos.ru&xdm_c=default1&xdm_p=1")
        ps.cookies.update(r.cookies)
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)
        
        # system_id: mos.ru
        r=my_get_post(ps.get,"https://www.mos.ru/api/oauth20/v1/frontend/json/ru/options")
        opts=json.loads(r.text)

        # надо: nonce signature timestamp
        #print("token request cookies:")
        #print_dict(ps.cookies)
        token_data={
                "system_id":opts["elk"]["system_id"],
                "nonce":opts["elk"]["nonce"],
                "timestamp":opts["elk"]["timestamp"],
                "signature":opts["elk"]["signature"]}
        ps.cookies["mos_user_segment"]="default"
        r=my_get_post(ps.post,self._data_url+"token", data=token_data)

        self._mos_ru_token=json.loads(r.text)["token"]

        print("mos.ru token:"+self._mos_ru_token)


    def ObtainPGUToken(self):
        ps=self._ps

        r=my_get_post(ps.get, "https://www.mos.ru/")
        ps.cookies.update(r.cookies)
        # obtain ADV-PHPSESSID
        ps.cookies["mos_user_segment"]="default"
        r=my_get_post(ps.get,
                "https://www.mos.ru/api/schmetterling/platforms/63301?ref=https://www.mos.ru/",
                headers={"referer":"https://www.mos.ru/"})
        ps.cookies.update(r.cookies)        
        # refresh ADV-PHPSESSID

        r=my_get_post(ps.get, "https://www.mos.ru/pgu/ru/services/link/2103/?onsite_from=3532")
        ps.cookies.update(r.cookies) 
        # obtain PHPSESSID
        # 302 redirect to https://oauth20.mos.ru/sps/oauth/oauth20/authorize
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)
        # 302 redirect to https://www.mos.ru/pgu/ru/oauth/?code=74...       
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)
        # 200 redirect to https://www.mos.ru/pgu/ru/services/link/2103/?onsite_from=3532
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)

        pdb.set_trace()


        # GET journal, obtain ELK token params
        # ps.cookies.update({"elk_token":"|"+self._mos_ru_token})
        r=my_get_post(ps.get, "https://www.mos.ru/pgu/ru/application/dogm/journal/")

        m=re.search('requestToken\((.*?)\)', r.text)
        opts=json.loads(m.group(1))
        print("pgu.mos.ru token params:")
        print(opts)
        ps.cookies["elk_token"]="|"+self._mos_ru_token
        r=my_get_post(ps.post,"https://my.mos.ru/data/token", data=opts)
        print("pgu.mos.ru token:")
        print(r.text)
        self._pgu_mos_ru_token = json.loads(r.text)["token"]
         

    def ListProfiles(self):
        """ Get list of diary accounts """
        milisecs=calendar.timegm(time.gmtime())*1000+random.randint(0,999)+1
        r=my_get_post(self._ps.get,self._data_url+self._mos_ru_token+"/profile/me/E_DIARY/?_="+str(milisecs))
        j=json.loads(r.text)
        r=[]
        for d in j["data"]:
            system=""
            try:
                system=d["SYSTEM"]
            except:
                pass
            a=DiaryProfile(d["LOGIN"],d["COMMENT"],d["PASSWORD"], system)
            
            r.append( a)


        return r

    def SelectProfile(self, p):
        """ Select profile """
        """ POST https://www.mos.ru/pgu/ru/application/dogm/journal/ """
        ps=self._ps
        params={ 
            "ajaxAction" : "get_token", 
            "ajaxModule" : "DogmJournal", 
            "data[login]": p.login, 
            "data[pass]" : p.password, 
            "data[system]" : p.system }
        ps.cookies["elk_token"]="null"+"|"+self._pgu_mos_ru_token
        ps.cookies["elk_id"]=""
        print("cookies:")
        print_dict(ps.cookies)
        print("params:")
        print_dict(params)
        ps.headers.update({'referer':"https://www.mos.ru/pgu/ru/application/dogm/journal/"})

        r=my_get_post(ps.post,"https://pgu.mos.ru/ru/application/dogm/journal/", data=params)
        print("Diary auth token:")
        print(r.text)
        pass



        """ https://dnevnik.mos.ru/lms/api/sessions """


    def ListAcademicYears(self):
        """ Get list of academic years """
        # https://dnevnik.mos.ru/core/api/academic_years?pid=#
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


class DiaryProfile:
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



