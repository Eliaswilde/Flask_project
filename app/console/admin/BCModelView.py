from flask_admin.contrib import sqla
from flask import Flask, url_for, redirect, render_template, request, flash
from flask.ext import login

class BCModelView(sqla.ModelView):
    list_template = 'bc_admin/model/list.html'
    edit_template = 'bc_admin/model/edit.html'
    create_template = 'bc_admin/model/create.html'

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect('/%s/'%self.admin.name)

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def render(self, template, **kwargs):
        kwargs['user'] = login.current_user
        return super(BCModelView, self).render(template, **kwargs)