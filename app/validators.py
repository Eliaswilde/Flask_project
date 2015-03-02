from wtforms import ValidationError

from services.database import db


class Unique(object):
    def __init__(self, model, field, message=None):
        if not message:
            message = u'Must be unique.'
        self.message = message
        self.model = model
        self.field = field

    def __call__(self, form, field):
        check = db.session.query(self.model).filter(
            self.field == field.data).first()
        if check:
            raise ValidationError(self.message)

unique = Unique
