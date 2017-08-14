#!env python3
# -*- coding: utf-8 -*- 

import requests
import calendar
import time
import random
import re
import json

import pdb

from gosuslugi_config import gosuslugi, dnevnik

MozWin='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'


def my_get_post(f,url, **kwargs):
    """ Try to GET or POST up to maxtries times. 
    If it fails - raise the exception.

    Used to counter bogus pgu.mos.ru responses. 
    Some times it does not work for the first (and second) connection. """
    maxtries=5
    attempt=0
    havedata=False
    print("request:",url)
    while attempt<maxtries:
        try:
            r=f(url,allow_redirects=False, **kwargs)
            return r
        except Exception as e:
            print(e)
            attempt+=1
    raise "Can not connect"

def print_dict(d):
    """ Pretty dictionary printer. For debugging """
    for key, value in d.items() :
            print ("["+key+"]=["+str(value)+"]")


def get_registered_journals(cfg):
    """ Get registered journals """
    ps = requests.Session()
    r = my_get_post(ps.get,"https://www.mos.ru/pgu/ru/application/dogm/journal/")

def mos_auth(cfg):
    """ authorization on mos.ru """
    ps=requests.Session()
    cfg["ps"]=ps
    ps.headers['User-Agent']=MozWin
    r=my_get_post(ps.get,"https://www.mos.ru")
    ps.cookies.update(r.cookies)
    r=my_get_post(ps.get,"https://www.mos.ru/api/oauth20/v1/frontend/json/ru/process/enter")
    ps.cookies.update(r.cookies)
    r=my_get_post(ps.get,r.headers['Location'])
    ps.cookies.update(r.cookies)
    r=my_get_post(ps.get,r.headers['Location'])
    ps.cookies.update(r.cookies)
    r=my_get_post(ps.get,r.headers['Location'])
    login_data={ 'j_username':cfg['login'], 'j_password' : cfg['password'] ,
            'accessType' : 'alias'}
    r= my_get_post(ps.post,"https://oauth20.mos.ru/sps/j_security_check",
            data=login_data)
    cfg['token']=ps.cookies['Ltpatoken2']
    ps.cookies.update(r.cookies)
    r=my_get_post(ps.get,r.headers['Location']) # wsauth
    ps.cookies.update(r.cookies)
    r=my_get_post(ps.get,r.headers['Location']) # result
    cfg['mostoken']=ps.cookies['mos_oauth20_token']




    print("response:")
    print(r)
    print("headers:")
    print_dict(r.headers)
    print("cookies:")
    print_dict(ps.cookies)


    print("----------8<---------")

def dnevnik_auth(cfg):
    ps=cfg["ps"]
    #ps.cookies["Ltpatoken2"]=cfg["token"]
    #ps.cookies["mos_oauth20_token"]=cfg["mostoken"]
    #ps.cookies["authtype"]="1"
    #ps.cookies["mos_id"]="CllGxlmRmORBZFNoK19+AgA="
    #ps.cookies["mos_user_segment"]="default"
    #pdb.set_trace()
    
    #milisecs=calendar.timegm(time.gmtime())*1000+random.randint(0,999)+1
    #r=my_get_post(ps.get,"https://my.mos.ru/static/js/elk-api-0.3.js?_="+str(milisecs))
    #milisecs=calendar.timegm(time.gmtime())*1000+random.randint(0,999)+1
    #r=my_get_post(ps.get,"https://my.mos.ru/static/js/cookie.js?_="+str(milisecs))

    milisecs=calendar.timegm(time.gmtime())*1000+random.randint(0,999)+1
    r=my_get_post(ps.get, "https://my.mos.ru/static/xdm/index.html?nocache="+str(milisecs)+"&xdm_e=https%3A%2F%2Fwww.mos.ru&xdm_c=default1&xdm_p=1")
    ps.cookies.update(r.cookies)
    r=my_get_post(ps.get,r.headers['Location'])
    ps.cookies.update(r.cookies)
    r=my_get_post(ps.get,r.headers['Location'])
    ps.cookies.update(r.cookies)
    r=my_get_post(ps.get,r.headers['Location'])
   
#    ps.cookies.update(r.cookies)
#    print_dict(ps.cookies)
    #ref="https://my.mos.ru/static/xdm/index.html?nocache="+str(milisecs)+"&xdm_e=https%3A%2F%2Fwww.mos.ru&xdm_c=default1&xdm_p=1"

    #r=my_get_post(ps.get,"https://my.mos.ru/static/js/easyXDM-2.4.17.1.min.js", headers={"referer" :    ref })
    #r=my_get_post(ps.get,"https://my.mos.ru/static/js/xdm.min.js", headers={"referer" :    ref })
    
    r=my_get_post(ps.get,"https://www.mos.ru/api/oauth20/v1/frontend/json/ru/options")
    opts=json.loads(r.text)

    # надо: nonce signature timestamp
    #print("token request cookies:")
    #print_dict(ps.cookies)
    token_data={"signature":opts["elk"]["signature"],"nonce":opts["elk"]["nonce"],
            "timestamp":opts["elk"]["timestamp"],"system_id":opts["elk"]["system_id"]}
    r=my_get_post(ps.post,"https://my.mos.ru/data/token", data=token_data)

    cfg["diary_token"]=json.loads(r.text)["token"]

def dnevnik_getlist(cfg):
    ps=cfg["ps"]
    milisecs=calendar.timegm(time.gmtime())*1000+random.randint(0,999)+1
    r=my_get_post(ps.get,"https://my.mos.ru/data/"+cfg["diary_token"]+"/profile/me/E_DIARY/?_="+str(milisecs))
    print("list:")
    print(r.text)
            


    






def get_dnevnik_token(cfg):
    """ Get auth_token from pgu.mos.ru applicable for dnevnik.mos.ru """

    MozWin='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'
    MozLin='Mozilla/5.0 (X11; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'

    # PGU session
    ps = requests.Session()

    ps.headers['User-Agent']=MozWin

    # 0. Gather PD_STATEFUL_{GUID} = 'pgu-ssl' cookie from pgu.mos.ru
    print("--------0----------")
    r=my_get_post(ps.get,"https://pgu.mos.ru/")
    print("cookies:")
    print_dict(ps.cookies)  
    print("Response headers:")
    print_dict(r.headers)
    print("Response:")
    print(r)



    # 1. Gather PHPSESSID cookie from pgu.mos.ru
    print("--------1----------")
    sessid_url='https://pgu.mos.ru/ru/'
    r=my_get_post(ps.get, 'https://pgu.mos.ru/ru/')
    PHPSESSID=ps.cookies['PHPSESSID']
    print_dict(ps.cookies)
    print("Response headers:")
    print_dict(r.headers)
    print("Response:")
    print(r)

    #ps.cookies["mos_id"]="CllGxlfzrOAIOCsqHSn0AgA="

    # 1.1 Gather PD_STATEFUL_{GUID} ='elk-ssl' cookie from my.mos.ru
    print("---1.1.---")
    # easyXDM is the first file accessed from my.mos.ru and the cookie comes
    # with it.
    r=my_get_post(requests.get, "https://my.mos.ru/static/js/easyXDM-2.4.17.1.js", 
            headers={"referer":"https://pgu.mos.ru/ru/"})
    print("first get")
    print_dict(r.cookies)
    ps.cookies.update(r.cookies)
    r=my_get_post(requests.get, "https://my.mos.ru/static/js/elk-api-0.3.js",
            headers={"referer":"https://pgu.mos.ru/ru/"})
    print("second get")
    print_dict(r.cookies)
    ps.cookies.update(r.cookies)
    print("elk cookies:")
    print_dict(ps.cookies)

    # 1.2 Gather mos_id cookie
    r=my_get_post(ps.get, "https://stats.mos.ru/counter.js")
    mos_id=r.cookies["mos_id"]
    print("mos_id:"+mos_id)

    # 1.5 get redirected from https://pgu.mos.ru/ru/auth/ to redirect.do
    print("--------1.5----------")
    sessid_url='https://pgu.mos.ru/ru/auth/'
    referer='https://pgu.mos.ru/ru/'
    ps.headers.update({'Referer':referer})
    r=my_get_post(ps.get,sessid_url)
    print_dict(ps.cookies)
    print("Response headers:")
    print_dict(r.headers)
    print("Response:")
    print(r)
    print("New location:")
    pdh_url=r.headers["Location"]
    print(r.headers["Location"])
#print(r.text)
     

    # 2. Get PD-H-SESSION-D cookie
    print("--------2----------")
    referer='https://pgu.mos.ru/ru/'
    ps.headers.update({'referer':referer})
    r=my_get_post(ps.get,pdh_url)

    cookies=ps.cookies
    PDH_ID=cookies['PD-H-SESSION-ID']
    print_dict(ps.cookies)
    print("Response headers:")
    print_dict(r.headers)
    print("Response:")
    print(r)
#print(r.text)

    # 3. Get JSESSIONID cookie, open_outer_login
    print("--------3----------")
    jsessid_url='https://login.mos.ru/eaidit/eaiditweb/openouterlogin.do'
    referer='https://login.mos.ru/eaidit/eaiditweb/redirect.do?redirectto=https%3A%2F%2Fpgu.mos.ru%2Fru%2Findex.php%3F'
    ps.cookies['login_href']="https://login.mos.ru/eaidit/eaiditweb/redirect.do?redirectto=https%3A%2F%2Fpgu.mos.ru%2Fru%2Findex.php%3F"
    ps.headers.update({'referer':referer})
    print("Session cookies before get")
    print_dict(ps.cookies)
    r=my_get_post(ps.get, jsessid_url)
    cookies=ps.cookies
    JSESSIONID=cookies['JSESSIONID']
    print_dict(ps.cookies)
    print("Response headers:")
    print_dict(r.headers)
    print("Response:")
    print(r)
#print(r.text)

    # 4. Send username/password. outer_login
    print("--------4----------")
    jsessid_url='https://login.mos.ru/eaidit/eaiditweb/outerlogin.do'
    referer='https://login.mos.ru/eaidit/eaiditweb/openouterlogin.do'
    ps.headers.update({'referer':referer})
    ps.cookies['login_href']="https://login.mos.ru/eaidit/eaiditweb/redirect.do?redirectto=https%3A%2F%2Fpgu.mos.ru%2Fru%2Findex.php%3F"
    credentials={'username':cfg['login'], 'password':cfg['password']}
    r=my_get_post( ps.post,jsessid_url, params=credentials)
    print("login headers:")
    print_dict(r.headers)
    print("Login respons cookies:")
    print_dict(r.cookies)
    print("Overall cookies:")
    print_dict(ps.cookies)
    print("Response:")
    print(r)
    #print(r.text)
    # Should be redirected to loginok.do here

    # 5. Gather cookies from loginok.do: Ltpatoken2, PD-H-SESSION-ID, PD-ID
    print("--------5----------")
    url='https://login.mos.ru/eaidit/eaiditweb/loginok.do'
    referer='https://login.mos.ru/eaidit/eaiditweb/openouterlogin.do'
    ps.headers.update({'referer':referer})
    r=my_get_post(ps.get,url)
    print("loginok headers:")
    print_dict(r.headers)
    print("Loginok respons cookies:")
    print_dict(r.cookies)
    print("Overall cookies:")
    print_dict(ps.cookies)

    print("Response:")
    print(r)

    # 6. Follow loginok.do redirect (should be to redirect.do)
    r=my_get_post(ps.get, r.headers["Location"])
    # 7. Follow second redirection (should be to /index.php?)
    r=my_get_post(ps.get, r.headers["Location"])

    # 8. Obtain elk_id cookie, refresh PD-ID cookie
    milisecs=calendar.timegm(time.gmtime())*1000+random.randint(0,999)+1
    print(milisecs)
    r=my_get_post(ps.get, "https://my.mos.ru/static/js/cookie.js?_="+str(milisecs))
    print_dict(ps.cookies)

    # 9. Obtain mysterious "nonce", "signature"
    print("----9----")
    referer="https://pgu.mos.ru/ru/index.php?"
    ps.headers.update({'referer':referer})
    r=my_get_post(ps.get, "https://pgu.mos.ru/ru/application/dogm/journal/")
    print("Response")
    print(r)
    m=re.search('requestToken\((.*?)\)', r.text)
    if m:
        print("nonce and signature:"+m.group(1))
    js=json.loads(m.group(1))
    print(js)
    print_dict(js)

    # 10. Obtain token from my.mos.ru/data/token
    ps.cookies.pop("login_href")
    ps.cookies.pop("JSESSIONID")
    ps.cookies.pop("PHPSESSID")

    cd=ps.cookies.get_dict()
    for k in cd:
        if ps.cookies[k]=="pgu-ssl":
            print("Clearing cookie:"+k)
            ps.cookies.pop(k)
            continue
        if ps.cookies[k]=="%2Feaidit":
            print("Clearing cookie:"+k)
            ps.cookies.pop(k)
            continue

    print("Sanitized cookies:")
    print_dict(ps.cookies)


    referer="https://my.mos.ru/static/xdm/index.html?xdm_e=https%3A%2F%2Fpgu.mos.ru&xdm_c=default1&xdm_p=1"
    ps.headers.update({'referer':referer})
    tokenparams={"system_id":js["system_id"], "timestamp":js["timestamp"],
            "nonce":js["nonce"], "signature":js["signature"]}
    print("Session headers")
    print_dict(ps.headers)
    print("Session cookies")
    print_dict(ps.cookies)
    r=my_get_post(ps.post,"https://my.mos.ru/data/token", data=js)
    print("Token:")
    print(r)
    print("Text:")
    print(r.text)

    pgu_token=json.loads(r.text)

    # 10.1 Get list of diaries

    r=my_get_post(ps.get,"https://my.mos.ru/data/"+pgu_token["token"]+"/profile/me/E_DIARY/?_=1475685723951")
    print("Diaries:")
    print(r.text)

    # 11. Obtain token for dnevnik

    dnevnikparams={ 
            "ajaxAction" : "get_token", 
            "ajaxModule" : "DogmJournal",
            "data[login]": dnevnik["login"],
            "data[pass]" : dnevnik["password"],
            "data[subsystem]" : "e" }
    ps.cookies["elk_token"]=ps.cookies["elk_id"]+"|"+pgu_token["token"]
    print_dict(ps.cookies)
    r=my_get_post(ps.post,"https://pgu.mos.ru/ru/application/dogm/journal/",
            data=dnevnikparams)
    print("Diary auth token:")
    print(r.text)

    diary_auth_token=json.loads(r.text)
    print(diary_auth_token["data"]["params"]["token"]  )

    # 12. Get Marks!
    ps.cookies["auth_token"]=diary_auth_token["data"]["params"]["token"]
    ps.cookies["profile_id"]="3096733"
    ps.cookies["profile_roles"]="student"
    ps.cookies["aid"]="4"
    ps.cookies["is_auth"]="true"
    ps.cookies["request_method"]="GET"
    print("Session cookies so far:")
    print_dict(ps.cookies)
    r=my_get_post(ps.get,"https://dnevnik.mos.ru/core/api/marks?created_at_from=03.10.2016&created_at_to=09.10.2016&page=1&per_page=50&pid=3096733&student_profile_id=3096733")
    print("Marks:")
    print(r.text)


    
#print(r.text)
     
#pgu_login='https://login.mos.ru/eaidit/eaiditweb/openouterlogin.do'
#print(r)
#print(r.headers)


#get_dnevnik_token(gosuslugi)

mos_auth(gosuslugi)
dnevnik_auth(gosuslugi)

dnevnik_getlist(gosuslugi)
