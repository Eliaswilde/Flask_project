from flask import url_for, jsonify
from flask.ext.admin import form
from flask.ext import login
from flask.ext.admin.contrib import sqla
from flask.ext import admin
from flask_admin import BaseView
from flask_admin.model import BaseModelView
from markupsafe import Markup
from wtforms import SelectField
from app.console.admin.BCBaseView import BCBaseView
from app.console.admin.BCModelView import BCModelView
from app.console.admin.fields.fields import BCDateField
from models.comment import Comment
from models.campaign import Campaign
from config import SQLALCHEMY_PAGINATE_MAX_RESULT
from services.database import db

class InboxView(BCBaseView):
    @admin.expose('/')
    def index(self):
        return self.render('account/inbox.html')
    
    @admin.expose('/list/')
    @admin.expose('/list/<int:page>/')
    def listview(self, page=1):
        return jsonify(self._render_inbox_items(page))

    @admin.expose('/seen/<int:page>/')
    def mark_seen(self, page):
        comment = Comment.query.get(int(page))
        data = {'success': 0}
        if comment:
            comment.is_shown_by_campaign_owner = True
            db.session.commit()
            data.update({'success': 1, 'message': 'Success'})
        return jsonify(data)

    def _render_inbox_items(self, page=1):
        comments_raw = Comment.query.join(Comment.campaign).filter(Campaign.user_id == login.current_user.id)\
            .order_by(Comment.date.desc())\
            .paginate(page, SQLALCHEMY_PAGINATE_MAX_RESULT, error_out=False)

        data = {}
        if comments_raw:
            data['meta'] = {
                'has_next': comments_raw.has_next,
                'has_prev': comments_raw.has_prev,
                'next_num': comments_raw.next_num,
                'prev_num': comments_raw.prev_num,
                'iter_pages': [p for p in comments_raw.iter_pages()],
                'current_page': comments_raw.page,
                'total_pages': comments_raw.pages,
                'total_items': comments_raw.total,
                'per_page': comments_raw.per_page
            }
            data['objects'] = list()
            for el in comments_raw.items:
                data['objects'].append(
                    {
                        'id': el.id,
                        'fromTo': el.user.first_name + ' ' + el.user.last_name,
                        'content': el.text,
                        'is_shown_by_campaign_owner': el.is_shown_by_campaign_owner,
                        'date': el.date.strftime('%d, %b'),
                        'campaign_id': el.campaign.id,
                        'campaign_title': el.campaign.title,
                        'campaign_short_description': el.campaign.short_description,
                        'campaign_thumbnail': el.campaign.thumbnail_url
                    }
                )
        return data
   # form_overrides = {
    #    'path': form.ImageUploadField
   # }
    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.

