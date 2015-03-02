import os
from StringIO import StringIO
import cStringIO
from sqlalchemy.orm import joinedload
from werkzeug.utils import redirect
from flask import url_for, request, jsonify, send_from_directory
from flask.ext import admin, login
from flask.ext.uploads import IMAGES, UploadSet, configure_uploads
from PIL import Image, ImageOps

from app import app, cloudinary
from services.database import db
from app.console.admin.BCBaseView import BCBaseView
from app.console.admin.forms.profileform import ProfileForm
from models import User, ContactInfo


AVATAR_SIZE = (128, 128)


avatars = UploadSet('avatars', IMAGES, default_dest=lambda app: 'uploads')
configure_uploads(app, (avatars, ))


class ProfileView(BCBaseView):
    @admin.expose('/', methods=('GET', 'POST'))
    def index(self):
        user = User.query.filter_by(id=login.current_user.id).options(
            joinedload(User.shipping_info), joinedload(User.billing_info)
        ).one()




        form = ProfileForm(request.form, user)

        if form.billing_equals_shipping == True:
            form.billing_info.optional = True

        if form.validate_on_submit():
            if not user.shipping_info:
                info = ContactInfo()
                db.session.add(info)
                user.shipping_info = info
            if not user.billing_info:
                info = ContactInfo()
                db.session.add(info)
                user.billing_info = info

            form.populate_obj(user)

            if form.data.get('billing_equals_shipping'):
                form.shipping_info.populate_obj(user, 'billing_info')

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('.index'))

        params = {
            'user': login.current_user,
            'form': form
        }
        return self.render('account/profile.html', **params)

    @admin.expose('/avatar/upload', methods=('POST', 'GET'))
    def upload_avatar(self):
        filename = request.files['Filedata']#avatars.save(request.files.get('Filedata'))
        #path = os.path.abspath(os.path.join('uploads', filename))
        #thumb_name = 'thumb.%s' % filename
        #thumb_path = os.path.join('uploads', thumb_name)

        #try:
        #    im = Image.open(path)
        #    im.thumbnail(AVATAR_SIZE, Image.ANTIALIAS)
        #    im.save(thumb_path, "JPEG")
        #except IOError as ex:
        #    print ex

        if filename:
                upload_result = cloudinary.upload_image(filename)
                return jsonify({'status': 'ok', 'avatar': upload_result["url"]})

        return jsonify({'status': 'ok', 'avatar': ''})

    def get_thumb_from_io(self,io_data):
        basewidth = 100
        io_data.seek(0)
        i = Image.open(io_data)
        i = ImageOps.fit(i, (basewidth,basewidth), Image.ANTIALIAS,0,(0.5,0))
        out_im2 = cStringIO.StringIO()
        i.save(out_im2,'PNG',optimize=True,quality=95)
        thumb_name = cloudinary.upload_image(out_im2)
        return thumb_name

    def cloudinary_upload_file(self,source_file):
        uploaded_data = cStringIO.StringIO()
        source_file.save(uploaded_data)
        thumb_url = self.get_thumb_from_io(uploaded_data)
        return (cloudinary.upload_image(uploaded_data),thumb_url)


    @admin.expose('/avatar')
    def send_file(self):
        user = User.query.filter_by(id=login.current_user.id).options(
            joinedload(User.shipping_info), joinedload(User.billing_info)
        ).one()

        return send_from_directory('uploads', user.avatar)

    @admin.expose('/avatar/preview/<file_name>')
    def file_preview(self, file_name):
        return send_from_directory('uploads', file_name)
