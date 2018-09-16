#!env python3

import dnevnik
import pdb

from pguauth import PGUAuthenticator
from dnevnik import Dnevnik

from gosuslugi_config import cfg
import json


auth = PGUAuthenticator(cfg)

# pdb.set_trace()
auth.Authenticate()

print("GOSUSLUGI TOKEN:")
print(auth.token)
#print(auth.mostoken)

d = Dnevnik(auth)
d.Authenticate()
d.ObtainPGUToken()
j = d.ListProfiles()
print(j[3])
d.SelectProfile(j[3])


