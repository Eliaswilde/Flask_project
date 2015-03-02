from random import randint
from flask import url_for
from flask.ext.admin import form
from flask.ext import login
from flask.ext.admin.contrib import sqla
from markupsafe import Markup
from sqlalchemy import func
from wtforms import SelectField
from app.console.admin.BCModelView import BCModelView
from app.console.admin.fields.fields import BCDateField
from models import Order, Reward, Campaign
from config import APP_BASE_URL


class ContributionsView(BCModelView):

    def get_query(self):
        return self.session.query(self.model).filter_by(user_id=login.current_user.id)

    def get_count_query(self):
        return self.session.query(func.count('*')).select_from(self.model).filter_by(user_id=login.current_user.id)

    def _list_thumb_thumbnail(view, context, model, name):
        return Markup('<img width="100" src="%s">' % model.campaign.thumbnail_url)

    def _list_campaign_link(view, context, model, name):
        return Markup('<a href="%(url)s">%(title)s</a>' % {"title" : model.campaign.title, "url" : url_for('campaign.index_by_vanity_url', vanity_url=model.campaign.vanity_url)} )




    #<a href="javascript:socialShare('https://www.facebook.com/sharer/sharer.php?u=http://beta.fanbacked.com/c/myrna-original-dramedy-television-series/', 520, 350)" class="btn btn-default fa fa-facebook btn-outline-inverse"></a>
    def _list_share_link(view, context, model, name):

        def _get_share_script(url):
            return "javascript:socialShare('%s', 520, 350)" % url

        url = APP_BASE_URL + url_for('campaign.index_by_vanity_url', vanity_url=model.campaign.vanity_url)
        facebook_url = _get_share_script('https://www.facebook.com/sharer/sharer.php?u=' + url)
        twitter_url = _get_share_script('https://twitter.com/share?url=' + url)
        google_url = _get_share_script('https://plus.google.com/share?url=' + url)
        return Markup('<input type="text" name="share-link" size="15" value="%(url)s" style="float: left; margin-right: 10px;"><div style="margin-top: 3px;">'
                      '<a href="%(facebook_url)s" class="btn btn-default fa fa-facebook" style="margin-right: 5px;"></a>'
                      '<a href="%(twitter_url)s" class="btn btn-default fa fa-twitter" style="margin-right: 5px;"></a>'
                      '<a href="%(google_url)s" class="btn btn-default fa fa-google-plus" style="margin-right: 5px;"></a></div>' % {"facebook_url" : facebook_url,"twitter_url" : twitter_url,"google_url" : google_url, "url" :url})

    column_labels = {
        'total': 'Amount',
    }

    column_formatters = {
        'campaign': _list_campaign_link,
        'reward': lambda v, c, m, p: m.reward.title if m.reward else 'Contribution Only',
        'referrals': lambda v, c, m, p: randint(1, 1000),
        'thumbnail': _list_thumb_thumbnail,
        'share' : _list_share_link,
    }

    can_edit=False
    can_delete=False
    can_create=False
    list_template = 'console/contributions_list.html'

    column_list = ('thumbnail', 'campaign', 'reward','total','referrals','share')

    column_sortable_list = (
        ('campaign', Campaign.title),
        ('reward', Reward.title),
        ('total', Order.cost),
    )


   # form_overrides = {
    #    'path': form.ImageUploadField
   # }
    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.

