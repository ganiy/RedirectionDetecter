from datetime import datetime
from time import strftime, gmtime

from mongoengine import *

connect(db="RedDec",host="localhost")

class Url(Document):
    sha256 = StringField()
    protocol = StringField()
    port = StringField()
    domain = StringField()
    path = StringField()
    query = StringField()
    screenshot = FileField()
    raw_data = StringField()
    broken = BooleanField()
    redirects = ListField(StringField())
    parser = StringField()

class RedirectionChain(Document):
    init_url = StringField()
    chain = ListField(ReferenceField("Url"),default=[])
    count = IntField(default=0)
