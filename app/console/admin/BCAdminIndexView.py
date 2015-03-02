from flask import Flask, url_for, redirect, render_template, request, flash
from flask.ext.admin import helpers, expose
from flask.ext import admin, login
from app.campaign.forms import LoginForm
from app.console.admin.forms.requestresetpasswordform import RequestResetPasswordForm
from app.console.admin.forms.resetpasswordform import ResetPasswordForm
from app.console.admin.forms.registrationform import RegistrationForm
from app.emails import send_password_reset, send_reset_password_complete
from models import User
from models.user import UserType
from services.database import db
from services.user_service import UserService

user_service = UserService()
class BCAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not self.is_accessible():
            return redirect('/%s/login/'%self.admin.name)
        return super(BCAdminIndexView, self).index()

    def _handle_view(self, name, **kwargs):
        pass


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

    def get_req_console_type(self,user_type):
        if UserType.Admin == user_type:
            return 'admin'
        elif UserType.Producer == user_type:
            return 'account'
        else:
            return 'profile'

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        if login.current_user.is_authenticated():
            if self.get_req_user_type() != login.current_user.user_type:
                return redirect('/%s/' % self.get_req_console_type(login.current_user.user_type))

        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User.query.filter_by(email=form.email.data, password=form.password.data).first()
            if user is None:
                flash('Invalid Username or Password')

            elif user.password != form.password.data:
                flash('Invalid Username or Password')
            else:
                login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        self._template_args['admin_name'] = self.admin.name
        print self.admin.name
        return self.render('shared/login.html')
        #return super(KagehAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()
            form.populate_obj(user)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))

        self._template_args['form'] = form
        return self.render('shared/register.html')

    @expose('/requestresetpassword/', methods=('GET', 'POST'))
    def requestresetpassword_view(self):
        form = RequestResetPasswordForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            if user is None:
                flash('User not found')
            else:
                send_password_reset(user)
                return redirect(url_for('.passwordemailsent_view'))

        self._template_args['form'] = form
        self._template_args['admin_name'] = self.admin.name
        return self.render('shared/request_reset_password.html')

    @expose('/passwordemailsent/', methods=('GET', 'POST'))
    def passwordemailsent_view(self):

        self._template_args['admin_name'] = self.admin.name
        return self.render('shared/password_email_sent.html')


    @expose('/resetpassword/', methods=('GET', 'POST'))
    def resetpassword_view(self):
        form = ResetPasswordForm(request.form)
        reset_hash = request.args.get('reset_hash')

        if request.method == 'GET':
            if reset_hash is not None:
                self._template_args['reset_hash'] = reset_hash
                user = user_service.get_by_reset_hash(reset_hash)
                if user is not None:
                    self._template_args['form'] = form
                    self._template_args['admin_name'] = self.admin.name
                    return self.render('shared/reset_password.html')
            else:
                return redirect(url_for('.requestresetpassword_view') + '?m=1')
        else:
            if helpers.validate_form_on_submit(form):
                user = user_service.get_by_reset_hash(str(form.reset_hash.data))
                if user is None:
                    flash('Something went wrong!')
                elif form.confirm.data != form.password.data:
                    flash('Passwords don\'t match')
                else:
                    user.password = form.confirm.data
                    db.session.commit()
                    send_reset_password_complete(user)
                    return redirect(url_for('.login_view') + '?m=0')

        self._template_args['reset_hash'] = reset_hash
        self._template_args['form'] = form
        self._template_args['admin_name'] = self.admin.name
        return self.render('shared/reset_password.html')

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.login_view'))

    def render(self, template, **kwargs):
        kwargs['user'] = login.current_user
        kwargs['profile_url'] = '/%s/%s/' % (self.admin.name, 'profileview' if self.get_req_user_type() == UserType.Producer else 'backerview')
        kwargs['inbox_url'] = '/%s/%s/' % (self.admin.name, 'inboxview' if self.get_req_user_type() == UserType.Producer else 'backerbox')
        return super(BCAdminIndexView, self).render(template, **kwargs)
