import time
import datetime

from wtforms import fields, widgets
from flask.ext.admin.babel import gettext
from flask.ext.admin._compat import text_type, as_unicode

from . import widgets as admin_widgets

__all__ = ['BCDateField']


class BCDateField(fields.Field):
    """
        A text field which stores a `datetime.time` object.
        Accepts time string in multiple formats: 20:10, 20:10:00, 10:00 am, 9:30pm, etc.
    """
    widget = admin_widgets.DatePickerWidget()

    def __init__(self, label=None, validators=None, formats=None,
                 default_format=None, widget_format=None, **kwargs):
        """
            Constructor

            :param label:
                Label
            :param validators:
                Field validators
            :param formats:
                Supported time formats, as a enumerable.
            :param default_format:
                Default time format. Defaults to '%H:%M:%S'
            :param widget_format:
                Widget date format. Defaults to 'hh:ii:ss'
            :param kwargs:
                Any additional parameters
        """
        super(BCDateField, self).__init__(label, validators, **kwargs)

        self.formats = formats or ('%H:%M:%S', '%H:%M','%Y-%m-%d',
                                   '%I:%M:%S%p', '%I:%M%p',
                                   '%I:%M:%S %p', '%I:%M %p')

        self.default_format = default_format or '%Y-%m-%d'
        self.widget_format = widget_format or 'hh:ii:ss'

    def _value(self):
        if self.raw_data:
            return u' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.default_format) or u''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = u' '.join(valuelist)

            if not date_str:
                return

            for format in self.formats:
                try:
                    timetuple = time.strptime(date_str, format)
                    self.data = datetime.date(timetuple.tm_year, timetuple.tm_mon, timetuple.tm_mday)
                    return
                except ValueError:
                    pass

            raise ValueError(gettext('Invalid time format'))
