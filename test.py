#!env python3

import dnevnik
import pdb

from colorama import init, Fore, Back, Style

from pguauth import PGUAuthenticator
from dnevnik import Dnevnik
from libmesh import MESHLibrary

from gosuslugi_config import cfg
import json

init()
print(f"Вход на {Style.BRIGHT}{Fore.WHITE}ГОС{Fore.BLUE}УСЛ{Fore.RED}УГИ{Style.RESET_ALL}: ",
        end="")
auth = PGUAuthenticator(cfg)

# pdb.set_trace()
if auth.Authenticate() :
    print(f"{Style.BRIGHT}{Fore.GREEN}OK{Style.RESET_ALL}")
else:
    print(f"{Style.BRIGHT}{Back.RED}Ошибка!{Style.RESET_ALL}")
    exit()


#print("GOSUSLUGI TOKEN:")
#print(auth.token)
#print(auth.mostoken)
print(f"Вход в электронный дневник: ", end="")
d = Dnevnik(auth)
if d.Authenticate():
    print(f"{Style.BRIGHT}{Fore.GREEN}OK{Style.RESET_ALL}")
else:
    print(f"{Style.BRIGHT}{Back.RED}Ошибка!{Style.RESET_ALL}")
    exit()
print(d._profile)
print("Вход осуществлён пользователем: %s %s %s" % (
    d._profile['first_name'],
    d._profile['middle_name'],
    d._profile['last_name']))
print("Роль: ", "Родитель" if d._profile['profiles'][0]['type'] == 'parent' else "Ученик")

students = d.ListStudents()

pprint(students)
#j = d.ListProfiles()
#print(j[3])
#d.SelectProfile(j[3])


