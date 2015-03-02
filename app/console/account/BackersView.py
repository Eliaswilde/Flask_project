import urllib
import urlparse
import StringIO
import csv
import time

from markupsafe import Markup
from sqlalchemy import func, and_
from wtforms import SelectField
from random import randint
from contextlib import closing
from boto.s3.connection import S3Connection

from flask import url_for, request, make_response, redirect
from flask.ext.admin import form
from flask.ext import login
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import filters, tools

from app.console.admin.BCModelView import BCModelView
from app.console.admin.fields.fields import BCDateField
from app.console.account.forms import SelectCampaignForm
from models import User, ContactInfo, Reward, Order, Campaign

from config import S3_ACCESS_KEY, S3_ACCESS_SECRET, S3_BUCKET_NAME, S3_MIN_CHUNK_SIZE

class CustomConverter(filters.FilterConverter):
    def convert(self, type_name, column, name, **kwargs):
        column_name = str(column)
        
        overrides = {
            'user.first_name': 'Backer First Name',
            'user.last_name': 'Backer Last Name',
            'reward.title': 'Reward',
            'contact_info.state': 'State',
            'contact_info.city': 'City'
        }
        
        if overrides.get(column_name):
            name = overrides[column_name]
        
        return super(CustomConverter, self).convert(type_name, column, name, **kwargs)
    
class ShippingAddressEqualFilter(filters.FilterEqual):
    def apply(self, query, value):
        return query.join((ContactInfo, Order.shipping_info_id==ContactInfo.id)).filter(self.column == value)

class ShippingAddressNotEqualFilter(filters.FilterNotEqual):
    def apply(self, query, value):
        return query.join((ContactInfo, Order.shipping_info_id==ContactInfo.id)).filter(self.column != value)

class ShippingAddressLikeFilter(filters.FilterLike):
    def apply(self, query, value):
        stmt = tools.parse_like_term(value)
        return query.join((ContactInfo, Order.shipping_info_id==ContactInfo.id)).filter(self.column.ilike(stmt))

class ShippingAddressNotLikeFilter(filters.FilterNotLike):
    def apply(self, query, value):
        stmt = tools.parse_like_term(value)
        return query.join((ContactInfo, Order.shipping_info_id==ContactInfo.id)).filter(~self.column.ilike(stmt))

def generate_shipping_address_filters(table, name):
    return (ShippingAddressEqualFilter(table, name),
            ShippingAddressNotEqualFilter(table, name),
            ShippingAddressLikeFilter(table, name),
            ShippingAddressNotLikeFilter(table, name))

def concat_url_params(url, params):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.urlencode(query)
    url = urlparse.urlunparse(url_parts)
    
    return url

class BackersView(BCModelView):
    EXPORT_BACKERS = 'backers'
    EXPORT_FULFILLMENT = 'fulfillment'
    
    can_create = False
    can_edit=False
    can_delete=False
    list_template = 'console/backers_list.html'
    campaign_id = None # This will be overwritten in get_query method

    column_labels = {
        'name': 'Backer Name',
        'cost': 'Contribution',
        'order_status_id': 'Payment',
        'is_shipping': 'Shipping',
        'order_status_id': 'Payment'
    }
    
    def _list_location(view, context, model, name):
        if not model.shipping_info:
            return '-'

        return '%s, %s %s' % (model.shipping_info.state, model.shipping_info.city, model.shipping_info.country)

    column_formatters = {
        'name': lambda v, c, m, p: '%s %s' % (m.user.first_name, m.user.last_name),
        'reward': lambda v, c, m, p: m.reward.title if m.reward else 'Contribution Only',
        'location': _list_location,
        'is_shipping': lambda v, c, m, p: 'Yes' if m.is_shipping else 'No',
        'referrals': lambda v, c, m, p: randint(1, 1000),
    }

    column_list = ('name', 'reward', 'cost', 'order_status_id', 'location', 'is_shipping', 'referrals')
    
    column_sortable_list = (
        ('name', User.first_name),
        ('reward', Reward.title),
        ('cost', Order.cost),
         'order_status_id',
         'is_shipping',
        ('location', 'shipping_info.city'),
    )
    
    column_filters = ('user.first_name', 'user.last_name', 'reward.title',
                      'cost', 'is_shipping', 'order_status_id')
    column_filters += generate_shipping_address_filters(ContactInfo.city, 'City')
    column_filters += generate_shipping_address_filters(ContactInfo.state, 'State')
    column_filters += generate_shipping_address_filters(ContactInfo.country, 'Country')

    filter_converter = CustomConverter()
    
    def _get_url(self, *args, **kwargs):
        url = super(BackersView, self)._get_url(*args, **kwargs)
        
        if request.args.get('campaign'):
            url = concat_url_params(url, {'campaign': request.args['campaign']})
        
        return url
    
    def get_query(self):
        campaigns = Campaign.query.filter(and_(Campaign.user_id==login.current_user.id,Campaign.published_document_id != None)).all()
        choices = [(unicode(c.id), c.title) for c in campaigns]
        
        campaigns_form = SelectCampaignForm(choices, request.args, csrf_enabled=False)
        
        if campaigns_form.validate():
            self.campaign_id = int(campaigns_form.data['campaign'])
        else:
            self.campaign_id = campaigns[0].id
        
        self._template_args['campaigns_form'] = campaigns_form
        return self.session.query(self.model).filter_by(campaign_id=self.campaign_id)
    
    def render(self, template, **kwargs):
        self._template_args['backers_report_url'] = concat_url_params(
                                        kwargs['return_url'], {'export': self.EXPORT_BACKERS})
        self._template_args['fulfillment_report_url'] = concat_url_params(
                                        kwargs['return_url'], {'export': self.EXPORT_FULFILLMENT})
        
        if request.args.get('export'):
            ACCESS_POLICY = 'public-read'
            connection = S3Connection(S3_ACCESS_KEY, S3_ACCESS_SECRET)
            bucket = connection.lookup(S3_BUCKET_NAME)
            file_name = '%s_report_%s_%s.csv' % (request.args['export'], login.current_user, int(time.time()))
            uploader = None
            
            with closing(StringIO.StringIO()) as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
                
                headers_common = ['Order Id', 'Backer Email', 'Backer First Name',
                           'Backer LastName', 'Reward', 'Contribution',
                           'Additional Contribution', 'Total', 'Datetime',
                           'Referrals']
                row_common = lambda order: [order.id, order.user.email, order.user.first_name,
                                     order.user.last_name, order.reward.title if order.reward else 'Contribution Only',
                                     order.cost, order.contribution, order.total,
                                     "{:%B %d %Y, %I:%M %p}".format(order.created_date), randint(1, 1000)]
                
                if request.args['export'] == self.EXPORT_BACKERS:
                    headers = headers_common
                    row = row_common
                elif request.args['export'] == self.EXPORT_FULFILLMENT:
                    headers = headers_common + ['Shipping Address']
                    row = lambda order: row_common(order) + (order.shipping_info and [order.shipping_info.as_string()] or [''])
                
                # Write column headers
                writer.writerow(headers)
                    
                # Write rows
                for order in kwargs['data']:
                    if csvfile.tell() >= S3_MIN_CHUNK_SIZE:
                        if not uploader:
                            uploader = bucket.initiate_multipart_upload(file_name, policy=ACCESS_POLICY)
                            chunks_counter = 1
                        
                        # Upload part
                        csvfile.seek(0)
                        uploader.upload_part_from_file(csvfile, chunks_counter)
                        
                        chunks_counter += 1
                        csvfile.truncate(0)
                    
                    writer.writerow(row(order))
                
                if not uploader:
                    report = bucket.new_key(file_name)
                    report.set_contents_from_file(csvfile, rewind=True)
                    report.set_acl(ACCESS_POLICY)
                    report_url = report.generate_url(expires_in=0, query_auth=False)
                else:
                    report = uploader.complete_upload()
                    report_url = report.location
                
                return redirect(report_url)
                
        return super(BackersView, self).render(template, **kwargs)
    
    def get_count_query(self):
        return self.session.query(func.count('*')).select_from(self.model).\
                                  filter_by(campaign_id=self.campaign_id)


    # form_overrides = {
    #    'path': form.ImageUploadField
    # }
    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
