from wtforms import widgets
from flask.globals import _request_ctx_stack
from flask.ext.admin.babel import gettext, ngettext
from flask.ext.admin import helpers as h

__all__ = ['DatePickerWidget', ]


class DatePickerWidget(widgets.TextInput):
    """
        Date picker widget.

        You must include bootstrap-datepicker.js and form.js for styling to work.
    """
    def __call__(self, field, **kwargs):
        kwargs['data-role'] = u'datepicker'
        kwargs['data-date-format'] = u'yyyy-mm-dd'
        kwargs['data-date-autoclose'] = u'true'
        kwargs['class'] = u'parsley-validated'
        return super(DatePickerWidget, self).__call__(field, **kwargs)