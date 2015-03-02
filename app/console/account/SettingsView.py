from flask.ext import admin, login
from flask import url_for, request, redirect
from sqlalchemy.orm import joinedload

from services.database import db
from app.console.admin.BCBaseView import BCBaseView
from app.console.admin.forms.settingsforms import ChangePasswordForm,\
    NotificationsForm, DeleteAccountForm
from models import User


class SettingsView(BCBaseView):
    def _render_settings_page(self, password_form=None, notif_form=None,
                              del_form=None):
        user = User.query.filter_by(id=login.current_user.id).one()

        password_form = password_form or ChangePasswordForm(request.form)
        notif_form = notif_form or NotificationsForm(request.form, user)
        del_form = del_form or DeleteAccountForm(request.form)

        params = {
            'user': user,
            'change_password_form': password_form,
            'notifications_form': notif_form,
            'delete_form': del_form,
        }
        return self.render('account/settings.html', **params)

    @admin.expose('/')
    def index(self):
        return self._render_settings_page()

    @admin.expose('/change_password', methods=('POST',))
    def change_password(self):
        user = User.query.filter_by(id=login.current_user.id).one()

        form = ChangePasswordForm(request.form)
        if form.validate_on_submit():
            user.password = form.data['new_password']
            db.session.add(user)
            db.session.commit()

            return redirect(url_for('.index'))

        return self._render_settings_page(password_form=form)

    @admin.expose('/save_notifications', methods=('POST',))
    def save_notifications(self):
        user = User.query.filter_by(id=login.current_user.id).one()

        form = NotificationsForm(request.form, user)
        if form.validate_on_submit():
            form.populate_obj(user)
            db.session.add(user)
            db.session.commit()

            return redirect(url_for('.index'))

        return self._render_settings_page(notif_form=form)

    @admin.expose('/delete_account', methods=('POST',))
    def delete_account(self):
        user = User.query.filter_by(id=login.current_user.id).one()

        form = DeleteAccountForm(request.form)
        if form.validate_on_submit():
            db.session.delete(user)
            db.session.commit()
            login.logout_user()

            return redirect(url_for('.index'))

        return self._render_settings_page(del_form=form)
