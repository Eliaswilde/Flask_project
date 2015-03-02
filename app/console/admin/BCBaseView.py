from flask_admin import BaseView
from flask_admin.contrib import sqla
from flask import Flask, url_for, redirect, render_template, request, flash
from flask.ext import login
from models.user import UserType


class BCBaseView(BaseView):

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect('/%s/'%self.admin.name)

    def is_accessible(self):
        if login.current_user.is_authenticated():
            if self.get_req_user_type() == login.current_user.user_type:
                return True
        return False

    def get_req_user_type(self):
        if self.admin.name == 'admin':
            return UserType.Admin
        elif self.admin.name == 'account':
            return UserType.Producer
        else:
            return UserType.Backer


    def render(self, template, **kwargs):
        kwargs['user'] = login.current_user
        kwargs['profile_url'] = '/%s/%s/' % (self.admin.name, 'profileview' if self.get_req_user_type() == UserType.Producer else 'backerview')
        kwargs['inbox_url'] = '/%s/%s/' % (self.admin.name, 'inboxview' if self.get_req_user_type() == UserType.Producer else 'backerbox')
        return super(BCBaseView, self).render(template, **kwargs)