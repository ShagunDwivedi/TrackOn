from flask_security import (
        RegisterForm,
        LoginForm
    )
from werkzeug.local import LocalProxy
from wtforms import StringField, ValidationError, validators

class ExtendedRegisterForm(RegisterForm):
    id = StringField('id')
    name = StringField('name')
