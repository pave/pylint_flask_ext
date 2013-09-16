"""
Test module to see how pylint handles imports from flask.ext.
"""
import datetime
from flask.ext import wtf
from flask.ext.wtf import StringField
import flask.ext.login
from flask.ext import login
import flask.ext.bla

datetime.foo = 'hi'

print datetime.foo

print wtf.Flboltolo
class MyForm(wtf.Form):
    """Test form"""
    field = StringField()

MyForm().validate_csrf_token()
foo.bar.baz = 'abc'
print flask.ext.login.login_user
print flask.ext.login.bloblobo
