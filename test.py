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

#print(auth.token)
#print(auth.mostoken)

d = Dnevnik(auth)
d.Authenticate()
j = d.ListDiaryAccounts()
print(j)


