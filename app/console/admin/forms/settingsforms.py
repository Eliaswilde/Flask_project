from flask_wtf import Form
from wtforms import ValidationError
from wtforms.fields import *
from wtforms.validators import *
from flask.ext import login


class ChangePasswordForm(Form):
    old_password = PasswordField(validators=[required()])
    new_password = PasswordField(validators=[required(), length(max=80)])
    confirm = PasswordField('Repeat Password', validators=[
        equal_to('new_password', message='Passwords must match')])

    def validate_old_password(self, field):
        user = login.current_user

        if not user:
            raise ValidationError('Please log in')

        if user.password != self.old_password.data:
            raise ValidationError('Invalid password')


class NotificationsForm(Form):
    notif_featured_newsletter = BooleanField('Monthly featured projects newsletter')
    notif_partner_events = BooleanField('Quarterly FanBacked partner exclusive events')
    notif_sneak_peeks = BooleanField('Occasional VIP campaign insider sneak peeks and exclusive rewards')

    notif_project_updates = BooleanField('Project updates')

    notif_backer_summary = BooleanField('New Backer Summary (Daily)')
    notif_comments = BooleanField('New Comments / Questions')
    notif_follower_summary = BooleanField('New Follower Summary (Daily)')


class DeleteAccountForm(Form):
    pass
