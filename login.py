#!env python3
# -*- coding: utf-8 -*- 

import requests

from gosuslugi_config import gosuslugi

maxtries=5


def my_get_post(f,url, **kwargs):
    attempt=0
    havedata=False
    print("regquest:",url)
    while attempt<maxtries:
        try:
            r=f(url,allow_redirects=False, **kwargs)
            return r
        except Exception as e:
            print(e)
            attempt+=1
    raise "Can not connect"


def print_dict(d):
    for key, value in d.items() :
            print ("["+key+"]=["+value+"]")


def get_dnevnik_token(cfg):

    s=requests.Session()
    MozWin='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'
    MozLin='Mozilla/5.0 (X11; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'

    # PGU session
    ps = requests.Session()
    # ELK session
    es = requests.Session()
    # Dnevnik session
    ds = requests.Session()

    ps.headers['User-Agent']=MozWin
    ds.headers['User-Agent']=MozWin
    es.headers['User-Agent']=MozWin


# 0. Начать собирать куки
    print("--------0----------")
    r=my_get_post(ps.get,"https://pgu.mos.ru/")
    print("cookies:")
    print_dict(ps.cookies)  
    print("Response headers:")
    print_dict(r.headers)
    print("Response:")
    print(r)

# 1. Добыть PHPSESSID
    print("--------1----------")
    sessid_url='https://pgu.mos.ru/ru/'
    r=my_get_post(ps.get, 'https://pgu.mos.ru/ru/')
    PHPSESSID=ps.cookies['PHPSESSID']
    print_dict(ps.cookies)
    print("Response headers:")
    print_dict(r.headers)
    print("Response:")
    print(r)
#print(r.text)

    ps.cookies["mos_id"]="CllGxlfzrOAIOCsqHSn0AgA="

# 1.5 https://pgu.mos.ru/ru/auth/
    print("--------1.5----------")
    sessid_url='https://pgu.mos.ru/ru/auth'
    referer='https://pgu.mos.ru/ru/'
    s.headers.update({'referer':referer})
    r=my_get_post(s.get,sessid_url)
    PHPSESSID=s.cookies['PHPSESSID']
    print_dict(s.cookies)
    print("Response headers:")
    print_dict(r.headers)
    print("Response:")
    print(r)
#print(r.text)
     

# 2. Добыть PD-H-SESSION-D
    print("--------2----------")
    pdh_url='https://login.mos.ru/eaidit/eaiditweb/redirect.do?redirectto=https://pgu.mos.ru/ru/index.php?'
    referer='https://pgu.mos.ru/ru/'
    s.headers.update({'referer':referer})
    r=my_get_post(s.get,pdh_url)

    cookies=s.cookies
    PDH_ID=cookies['PD-H-SESSION-ID']
    print_dict(s.cookies)
    print("Response headers:")
    print_dict(r.headers)
    print("Response:")
    print(r)
#print(r.text)

# 3. Добыть JSESSIONID
    print("--------3----------")
    jsessid_url='https://login.mos.ru/eaidit/eaiditweb/openouterlogin.do'
    referer='https://login.mos.ru/eaidit/eaiditweb/redirect.do?redirectto=https%3A%2F%2Fpgu.mos.ru%2Fru%2Findex.php%3F'
    s.cookies['login_href']="https://login.mos.ru/eaidit/eaiditweb/redirect.do?redirectto=https%3A%2F%2Fpgu.mos.ru%2Fru%2Findex.php%3F"
    s.headers.update({'referer':referer})
    r=my_get_post(s.get, jsessid_url)
    cookies=s.cookies
    JSESSIONID=cookies['JSESSIONID']
    print_dict(s.cookies)
    print("Response headers:")
    print_dict(r.headers)
    print("Response:")
    print(r)
#print(r.text)

# 4. Предъявить логин-пароли
    print("--------4----------")
    jsessid_url='https://login.mos.ru/eaidit/eaiditweb/openouterlogin.do'
    referer='https://login.mos.ru/eaidit/eaiditweb/openouterlogin.do'
    s.headers.update({'referer':referer})
    s.cookies['login_href']="https://login.mos.ru/eaidit/eaiditweb/redirect.do?redirectto=https%3A%2F%2Fpgu.mos.ru%2Fru%2Findex.php%3F"
    credentials={'username':cfg['login'], 'password':cfg['password']}
    r=my_get_post( s.post,jsessid_url, params=credentials)
    print("login headers:")
    print_dict(r.headers)
    print("Login respons cookies:")
    print_dict(r.cookies)
    print("Overall cookies:")
    print_dict(s.cookies)
    print("Response:")
    print(r)
#print(r.text)

# 5. Переход на loginok
    print("--------5----------")
    url='https://login.mos.ru/eaidit/eaiditweb/loginok.do'
    referer='https://login.mos.ru/eaidit/eaiditweb/openouterlogin.do'
    s.headers.update({'referer':referer})
    r=my_get_post(s.get,url)
    print("loginok headers:")
    print_dict(r.headers)
    print("Loginok respons cookies:")
    print_dict(r.cookies)
    print("Overall cookies:")
    print_dict(s.cookies)

    print("Response:")
    print(r)
#print(r.text)
     
#pgu_login='https://login.mos.ru/eaidit/eaiditweb/openouterlogin.do'
#print(r)
#print(r.headers)


get_dnevnik_token(gosuslugi)
