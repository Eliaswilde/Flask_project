from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory
from flask.ext import login
from app.campaign.forms import LoginForm, SignupForm

www = Blueprint('www', __name__, static_folder="../static", template_folder="../templates")

@www.route("/")
def index():
	return render_footer_template("www/index.html")

@www.route("/about/")
def about():
	return render_footer_template("www/index.html")

@www.route("/faq/")
def faq():
    return render_footer_template("campaign/faq.html")

@www.route("/terms/")
def terms():
	return render_footer_template("campaign/terms.html")

@www.route("/privacy/")
def privacy():
	return render_footer_template("campaign/privacy.html")

@www.route("/contact/")
def contact():
	return render_footer_template("www/index.html")

@www.route("/discover/")
def discover():
	return render_template("www/index.html")

@www.route("/create/")
def create():
	return render_template("www/index.html")

@www.route('/producer-application', methods=['POST', "GET"])
def producer_application():
    return render_footer_template('campaign/producer_application.html')

def render_footer_template(template_path):
    login_form = LoginForm()
    signup_form = SignupForm()
    user = (login.current_user.is_authenticated() and [login.current_user] or [None])[0]
    return render_template(template_path, login_form=login_form, signup_form=signup_form)

@www.route('/www/static/css/<path:file_name>')
def css(file_name):
	return send_from_directory('app/static/www/css/', file_name)

@www.route('/www/static/js/<path:file_name>')
def js(file_name):
	return send_from_directory('app/static/www/js', file_name)

@www.route('/www/static/img/<path:file_name>')
def img(file_name):
	return send_from_directory('app/static/www/img', file_name)

@www.route('/www/static/html/<path:file_name>')
def html(file_name):
	return send_from_directory('app/static/www/html', file_name)

@www.route('/www/static/fonts/<path:file_name>')
def font(file_name):
	return send_from_directory('app/static/www/fonts', file_name)

@www.route('/favicon.ico')
def favicon():
	return send_from_directory('app/static','favicon.ico')
