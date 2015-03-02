import datetime
import json
from flask import Flask, url_for, redirect, render_template, request, flash
from flask.ext import admin, login
from sqlalchemy import and_
from app import BCAdminIndexView
from models import Campaign
from services.database.database import mongodb
from services.stats_service import get_visits_daily


class DashboardView(BCAdminIndexView):
    @admin.expose('/', methods=('GET', 'POST'))
    def index(self):

        if not self.is_accessible():
            return redirect('/%s/login/'%self.admin.name)

        campaigns = Campaign.query.filter(and_(Campaign.user_id==login.current_user.id,Campaign.published_document_id != None)).first()

        return self.render('account/dashboard.html',campaigns=campaigns)


    @admin.expose('/visitor_stats/', methods=('GET','POST'))
    def visitor_stats(self):
        now = datetime.datetime.utcnow()
        start_time = datetime.datetime.utcnow() - datetime.timedelta(days=60)
        cursor1 = get_visits_daily(mongodb,start_time,now,1)
        data = {}
        for record in cursor1:
            data = json.dumps(record['daily'], ensure_ascii=False)

        return data


