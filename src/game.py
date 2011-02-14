'''
Created on Feb 13, 2011

@author: Razvan
'''

import datetime
from google.appengine.ext import db

class Player(db.Model):
    name = db.StringProperty(required=True)
    ip_address = db.StringProperty()
    listen_port = db.StringProperty()
    last_online = db.DateTimeProperty()
    online = db.BooleanProperty()


    
    