from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory

console = Blueprint('console', __name__, static_folder="../static", template_folder="../templates", url_prefix="/console")

@console.route("/")
def index():
	return render_template("console/index.html")


@console.route('/css/<path:file_name>')
def css(file_name):
    print file_name
    return send_from_directory('app/static/console/css/', file_name)

@console.route('/js/<path:file_name>')
def js(file_name):
	return send_from_directory('app/static/console/js', file_name)

@console.route('/lib/<path:file_name>')
def lib(file_name):
	return send_from_directory('app/static/console/lib', file_name)

@console.route('/img/<path:file_name>')
def img(file_name):
	return send_from_directory('app/static/console/img', file_name)

@console.route('/static/html/<path:file_name>')
def html(file_name):
	return send_from_directory('app/static/console/html', file_name)

@console.route('/static/fonts/<path:file_name>')
def font(file_name):
	return send_from_directory('app/static/console/fonts', file_name)

