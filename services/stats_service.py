from datetime import datetime, time


def get_visits_daily(db,start_date,end_date,campaign_id):
    return db.visitor_stats.daily.find(
     {
         'metadata.date': { '$gte': start_date, '$lte': end_date },
         'metadata.campaign_id': campaign_id },
     { 'metadata.date': 1, 'daily': 1 } ,
         sort=[('metadata.date', 1)])

def log_visit(db, dt_utc,user_id, campaign_id):

    # Update daily stats doc
    id_daily = dt_utc.strftime('%Y%m%d/') + 'visits/' + str(campaign_id)
    day = dt_utc.day
    hour = dt_utc.hour
    minute = dt_utc.minute

    # Get a datetime that only includes date info
    d = datetime.combine(dt_utc.date(), time.min)
    query = {
        '_id': id_daily,
        'metadata': { 'date': d, 'campaign_id': campaign_id,'user_id':user_id } }
    update = { '$inc': {
            'daily.%d' % (day,): 1,
            'hourly.%d' % (hour,): 1,
            'minute.%d.%d' % (hour,minute): 1 } }
    db.visitor_stats.daily.update(query, update, upsert=True)

    # Update monthly stats document
    id_monthly = dt_utc.strftime('%Y%m/')  + 'visits/' + str(campaign_id)
    day_of_month = dt_utc.day
    query = {
        '_id': id_monthly,
        'metadata': {
            'date': d.replace(day=1),
            'campaign_id': campaign_id,
            'user_id':user_id} }
    update = { '$inc': {
            'daily.%d' % day_of_month: 1} }
    db.visitor_stats.monthly.update(query, update, upsert=True)

def log_backer(db, dt_utc, campaign_id, backer_id,backer_name):

    # Update daily stats doc
    id_daily = dt_utc.strftime('%Y%m%d/backers/') + campaign_id
    hour = dt_utc.hour
    minute = dt_utc.minute

    # Get a datetime that only includes date info
    d = datetime.combine(dt_utc.date(), time.min)
    query = {
        '_id': id_daily,
        'metadata': { 'date': d, 'campaign_id': campaign_id, 'backer_id': backer_id, 'backer_name': backer_name  } }
    update = { '$inc': {
            'hourly.%d' % (hour,): 1,
            'minute.%d.%d' % (hour,minute): 1 } }
    db.stats.daily.update(query, update, upsert=True)

    # Update monthly stats document
    id_monthly = dt_utc.strftime('%Y%m/backers/') + campaign_id
    day_of_month = dt_utc.day
    query = {
        '_id': id_monthly,
        'metadata': {
            'date': d.replace(day=1),
            'campaign_id': campaign_id,
            'backer_id': backer_id,
            'backer_name': backer_name } }
    update = { '$inc': {
            'daily.%d' % day_of_month: 1} }
    db.stats.monthly.update(query, update, upsert=True)


def log_sale(db, dt_utc, campaign_id, amount):

    # Update daily stats doc
    id_daily = dt_utc.strftime('%Y%m%d/sales/') + campaign_id
    hour = dt_utc.hour
    minute = dt_utc.minute

    # Get a datetime that only includes date info
    d = datetime.combine(dt_utc.date(), time.min)
    query = {
        '_id': id_daily,
        'metadata': { 'date': d, 'campaign_id': campaign_id } }
    update = { '$inc': {
            'hourly.%d' % (hour,): amount,
            'minute.%d.%d' % (hour,minute): amount } }
    db.stats.daily.update(query, update, upsert=True)

    # Update monthly stats document
    id_monthly = dt_utc.strftime('%Y%m/sales/') + campaign_id
    day_of_month = dt_utc.day
    query = {
        '_id': id_monthly,
        'metadata': {
            'date': d.replace(day=1),
            'campaign_id': campaign_id } }
    update = { '$inc': {
            'daily.%d' % day_of_month: amount} }
    db.stats.monthly.update(query, update, upsert=True)