import string
import random
from helpers.paypal_classic import CreateChainedPayment, VerifyPayyment
from models import Campaign, User, Comment
from decimal import Decimal
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, jsonify, escape, session, json
import paypalrestsdk
from sqlalchemy import and_
from app.console.admin.forms.checkoutform import CheckoutForm
from config import APP_BASE_URL, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from models import Campaign, User, Reward, Order, ContactInfo
from .forms import LoginForm, SignupForm
from flask.ext import login
from models.campaign import CampaignUpdate
from models.order import OrderStatus
from models.user import UserType
from services.campaign_service import CampaignService
from services.database import db
from config import SQLALCHEMY_PAGINATE_MAX_RESULT
from flask_oauth import OAuth


oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

campaign = Blueprint('campaign', __name__, static_folder="../static", template_folder="../templates", url_prefix="/c")
campaign_service = CampaignService()
@campaign.route('/fb_login')
def fb_login():
    """ Log in / register user using facebook """

    return facebook.authorize(callback=url_for('campaign.facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@campaign.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    """ Handle facebook callback. Create/update user. """

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    fb_user = facebook.get('/me')
    
    # Checking if the user is already registered
    user = User.query.filter_by(email=fb_user.data['email']).first()
    if user:
        # Existing user
        is_new = False
    else:
        # New user
        user = User(email=fb_user.data['email'])
        is_new = True
    
    # Add/update user data
    user.first_name = fb_user.data['first_name']
    user.last_name = fb_user.data['last_name']
    
    if is_new:
        # Generating password if the user is new
        #app.emails.send_backer_account_created(user)
        user.password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    
    db.session.add(user)
    db.session.commit()
    
    login.login_user(user)
    
    # TODO: Change the redirect url
    return redirect(request.args['next'])

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@campaign.route("/<int:campaign_id>/")
def index(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).one()
    return redirect(url_for('.index_by_vanity_url',vanity_url=campaign.vanity_url))

@campaign.route("/<string:vanity_url>/")
def index_by_vanity_url(vanity_url):
    login_form = LoginForm()
    signup_form = SignupForm()
    campaign = Campaign.query.filter_by(vanity_url=vanity_url).one()
    user = (login.current_user.is_authenticated() and [login.current_user] or [None])[0]

    comments = campaign.comments.filter(Comment.is_hidden==False).order_by(Comment.date.desc()).\
        paginate(1, SQLALCHEMY_PAGINATE_MAX_RESULT)

    support_link = APP_BASE_URL + url_for('.support_get',vanity_url=vanity_url) + "?reward_id="
    share_link = APP_BASE_URL + url_for('.index_by_vanity_url',vanity_url=vanity_url)
    print support_link


    backers = Order.query.filter(and_(Order.order_status_id==OrderStatus.Success,Order.campaign_id==campaign.id)).order_by(Order.created_date.desc())[0:100]
    is_backer=False
    for i in backers:
       if user is not None and user.id==i.user.id:
           is_backer=True
           break
           
    raw_data = campaign_service.get_draft(campaign.published_document_id)['data']
    return render_template("campaign/index.html", model=campaign, login_form=login_form,
                           signup_form=signup_form, user=user,support_link=support_link,share_link=share_link,backers=backers,comments=comments,vanity_url=vanity_url,is_backer=is_backer,raw_data=raw_data)

@campaign.route("/<string:vanity_url>/update/create/", methods=['POST'])
def create_update(vanity_url):
    campaign = Campaign.query.filter_by(vanity_url=vanity_url).one()

    if not can_do_update(campaign):
        return jsonify({'status': 'failed'})
    
    is_exclusive=False
    if "exclusive" in request.values.keys():
        if request.values['exclusive']=="true":
            is_exclusive=True
        
    cu = CampaignUpdate(
        user_id=campaign.user_id,
        campaign_id=campaign.id,
        text=request.values["text"],
        is_exclusive=is_exclusive
    )

    db.session.add(cu)
    db.session.commit()

    return jsonify({'status': 'success', 'update_id':cu.id})

@campaign.route("/<string:vanity_url>/update/edit/", methods=['POST'])
def edit_update(vanity_url):
    campaign = Campaign.query.filter_by(vanity_url=vanity_url).one()

    if not can_do_update(campaign):
        return jsonify({'status': 'failed'})

    update_id = request.values["update_id"]
    update = CampaignUpdate.query.filter_by(id=update_id).first()

    if(update.campaign_id != campaign.id):
        return jsonify({'status': 'failed'})

    update.text=request.values["text"]
    db.session.commit()

    return jsonify({'status': 'success'})

@campaign.route("/<string:vanity_url>/update/delete/", methods=['POST'])
def delete_update(vanity_url):
    campaign = Campaign.query.filter_by(vanity_url=vanity_url).one()

    if not can_do_update(campaign):
        return jsonify({'status': 'failed'})

    update_id = request.values["update_id"]
    update = CampaignUpdate.query.filter_by(id=update_id).first()

    if(update.campaign_id != campaign.id):
        return jsonify({'status': 'failed'})

    update.is_active=False
    db.session.commit()

    return jsonify({'status': 'success'})

def can_do_update(campaign):
    current_user = (login.current_user.is_authenticated() and [login.current_user] or [None])[0]

    if(current_user is None):
        return False

    if(current_user.id != campaign.user_id and current_user.user_type != UserType.Admin):
        return False

    return True


@campaign.route("/<string:vanity_url>/support/", methods=['GET'])
def support_get(vanity_url):
    login_form = LoginForm()
    signup_form = SignupForm()
    campaign = Campaign.query.filter_by(vanity_url=vanity_url).one()
    form = CheckoutForm()

    current_reward = None
    if request.args.get('reward_id'):
        current_reward = Reward.query.filter_by(id=request.args.get('reward_id')).first()
        form.reward_id.data = str(current_reward.id)

    current_user = (login.current_user.is_authenticated() and [login.current_user] or [None])[0]
    return render_template("campaign/purchase.html", model=campaign, login_form=login_form, signup_form=signup_form,form=form,current_reward=current_reward, user=current_user)


@campaign.route("/<string:vanity_url>/support/cancel/", methods=['GET'])
def support_cancel(vanity_url):
    token = request.args.get('token')

    payment_id = session['paypal_payment_id']
    order = Order.query.filter_by(paypal_order_id=payment_id).first()
    order.order_status_id=OrderStatus.Canceled
    db.session.commit()

    return redirect(url_for('.index_by_vanity_url',vanity_url=vanity_url))

@campaign.route("/<string:vanity_url>/support/success/", methods=['GET'])
def support_success(vanity_url):
    payer_id = request.args.get('PayerID')
    token = request.args.get('token')
    print token

    payment_id = session['paypal_payment_id']

    payment = paypalrestsdk.Payment.find(payment_id)
    payment.execute({"payer_id": payer_id})

    order = Order.query.filter_by(paypal_order_id=payment_id).first()
    order.order_status_id=OrderStatus.Success
    db.session.commit()
    share_link = APP_BASE_URL + url_for('.index_by_vanity_url',vanity_url=vanity_url)
    login_form = LoginForm()
    signup_form = SignupForm()
    campaign = Campaign.query.filter_by(vanity_url=vanity_url).one()
    share_url = return_url = APP_BASE_URL + url_for('.index_by_vanity_url',vanity_url=vanity_url)+"?usr_ref="+"aSdso90ssp"
    current_user = (login.current_user.is_authenticated() and [login.current_user] or [None])[0]

    return render_template("campaign/success.html", model=campaign, login_form=login_form, signup_form=signup_form,share_url=share_url,user=current_user,order=order,share_link=share_link)


    #payment_id = session['paypal_payment_id']
    #print "payment_id: " + payment_id
    ##payment = paypalrestsdk.Payment.find(payment_id)
    ##payment.execute({"payer_id": payer_id})
    #payment_status = VerifyPayyment(payment_id)
    #
    #if payment_status['status'] == 'COMPLETED':
    #    print 'Pay status is COMPLETED'
    #    order = Order.query.filter_by(paypal_order_id=payment_id).first()
    #    order.order_status_id=OrderStatus.Success
    #    db.session.commit()
    #
    #login_form = LoginForm()
    #signup_form = SignupForm()
    #campaign = Campaign.query.filter_by(vanity_url=vanity_url).one()
    #share_url = return_url = APP_BASE_URL + url_for('.index_by_vanity_url',vanity_url=vanity_url)+"?usr_ref="+"aSdso90ssp"
    #current_user = (login.current_user.is_authenticated() and [login.current_user] or [None])[0]
    #
    #return render_template("campaign/success.html", model=campaign, login_form=login_form, signup_form=signup_form,share_url=share_url,user=current_user,order=order)


@campaign.route("/<string:vanity_url>/support/payment/", methods=['POST','GET'])
def payment_post(vanity_url):

    login_form = LoginForm()
    signup_form = SignupForm()
    current_user = (login.current_user.is_authenticated() and [login.current_user] or [None])[0]
    share_url = return_url = APP_BASE_URL + url_for('.index_by_vanity_url',vanity_url=vanity_url)+"?usr_ref="+"aSdso90ssp"

    return render_template("campaign/purchase_payment.html",  login_form=login_form, signup_form=signup_form,share_url=share_url,user=current_user)

@campaign.route("/<string:vanity_url>/support/", methods=['POST'])
def support_post(vanity_url):
    login_form = LoginForm()
    signup_form = SignupForm()
    campaign = Campaign.query.filter_by(vanity_url=vanity_url).one()

    checkout_form = CheckoutForm(request.form)
    current_user = (login.current_user.is_authenticated() and [login.current_user] or [None])[0]
    reward = None
    if checkout_form.reward_id.data:
        reward = Reward.query.filter_by(id=checkout_form.reward_id.data).first()

    if current_user:
        checkout_form.anon_info.form_class.is_form_optional=True

    if reward and reward.is_shipping_required:
        checkout_form.shipping_info.form_class.is_form_optional=False
    else:
        checkout_form.shipping_info.form_class.is_form_optional=True

    if not checkout_form.validate_on_submit():
        return render_template("campaign/purchase.html", model=campaign, login_form=login_form, signup_form=signup_form,form=checkout_form,current_reward=reward,user=current_user)

    if current_user == None:
        current_user = User(
            password=str(uuid.uuid4()),
            email=checkout_form.anon_info.email.data,
            user_type=UserType.Backer,
            is_anonymous=True
        )
        db.session.add(current_user)
        db.session.commit()

    total = float(reward.cost + reward.cost) if reward else float(checkout_form.contributionamount.data)
    shipping_fee = 0

    if reward and reward.is_shipping_required:
        shipping_fee = reward.shipping_fee if checkout_form.shipping_info.country == 'US' else reward.international_shipping_fee

    if(reward):
        if(float(checkout_form.contributionamount.data) > float(reward.cost + reward.cost)):
            total = float(checkout_form.contributionamount.data)
    else:
        total = float(checkout_form.contributionamount.data)

    order = Order(
        cost = reward.cost if reward else 0,
        tax = 0,
        contribution = checkout_form.contributionamount.data,
        shipping = shipping_fee,
        total = float(total),
        order_status_id = OrderStatus.Created,
        is_shipping=reward.is_shipping_required if reward else False,
        is_private=False,
        shipping_date=reward.delivery_date if reward else None,
        user_id=current_user.id,
        campaign_id=campaign.id,
        reward_id=reward.id if reward else None,
        paypal_order_id=''
    )

    if reward and reward.is_shipping_required:
        contact = ContactInfo()
        contact.address = checkout_form.shipping_info.address.data
        contact.city = checkout_form.shipping_info.city.data
        contact.state = ""#checkout_form.shipping_info.state.data
        contact.postal_code = checkout_form.shipping_info.postal_code.data
        contact.country = checkout_form.shipping_info.country.data
        order.shipping_info = contact
    db.session.add(order)
    db.session.commit()

    raw_data = campaign_service.get_draft(campaign.published_document_id)['data']

    return_url = APP_BASE_URL + url_for('.support_success',vanity_url=vanity_url)
    cancel_url = APP_BASE_URL + url_for('.support_cancel',vanity_url=vanity_url)

    payment = paypalrestsdk.Payment({
      "intent": "sale",
      "payer": {
        "payment_method": "paypal" },
      "redirect_urls": {
        "return_url": str(return_url),
        "cancel_url": str(cancel_url)
      },
      "transactions": [ {
        "amount": {
          "total": '%.2f' % order.total,
          "currency": "USD" },
        "description": str(escape(reward.title if reward else 'Fanbacked Contribution')) } ] } )


    response = payment.create()
    if response:
        payment_id = payment.id
        session['paypal_payment_id'] = payment_id
        order.paypal_order_id = payment_id
        order.order_status_id=OrderStatus.Submitted
        db.session.commit()
        for link in payment.links:
            if link.method == "REDIRECT":
              redirect_url = link.href
              return redirect(redirect_url)
    else:
        print "Paypal response failed: " + str(response)
        print payment
    return redirect(url_for('.support_get',vanity_url=vanity_url))


    #total_fee_percent = campaign.total_fee_percent
    #
    #primary_total = order.total
    #secondary_total = (primary_total * total_fee_percent)
    #
    ##paypal_email = raw_data['form_paid']['paypal_email']
    #
    ##paypal_results = CreateChainedPayment(primary_total,paypal_email,secondary_total,return_url,cancel_url)
    #
    ##payment = paypalrestsdk.Payment({
    ##  "intent": "sale",
    ##  "payer": {
    ##    "payment_method": "paypal" },
    ##  "redirect_urls": {
    ##    "return_url": str(return_url),
    ##    "cancel_url": str(cancel_url)
    ##  },
    ##  "transactions": [ {
    ##    "amount": {
    ##      "total": '%.2f' % order.total,
    ##      "currency": "USD" },
    ##    "description": str(escape(reward.title if reward else 'Fanbacked Contribution')) } ] } )
    ##
    ##
    ##response = payment.create()
    #if paypal_results:
    #    payment_id = paypal_results['payKey']
    #    session['paypal_payment_id'] = payment_id
    #    order.paypal_order_id = payment_id
    #    order.order_status_id=OrderStatus.Submitted
    #    db.session.commit()
    #    return redirect(paypal_results['url'])
    #else:
    #    print "Paypal response failed: " + str(paypal_results)
    #    print paypal_results
    #return redirect(url_for('.support_get',vanity_url=vanity_url))
    #return render_template("campaign/purchase.html", model=campaign, login_form=login_form, signup_form=signup_form)

@campaign.route("/login", methods=['POST'])
def do_login():
    form = LoginForm()
    if not form.validate():
        return jsonify({
            'status': 'error',
            'fields_errors': form.errors
        })
    
    user = User.query.filter_by(email=form.email.data, password=form.password.data).first()
    if not user:
        return jsonify({'status': 'error', 'general_error': 'Email and password do not match'})
    
    if not login.current_user.is_authenticated():
        login.login_user(user)
    return jsonify({'status': 'success'})

@campaign.route("/logout")
def logout():
    login.logout_user()

    return redirect(url_for('.index', campaign_id=request.args.get('campaign_id')))

@campaign.route("/signup", methods=['POST'])
def signup():
    form = SignupForm()
    if not form.validate():
        return jsonify({
            'status': 'error',
            'fields_errors': form.errors
        })
    
    user = User(first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.email.data,
                email=form.email.data,
                password=form.password.data)
    #app.emails.send_backer_account_created(user)
    db.session.add(user)
    db.session.commit()
    
    login.login_user(user)
    
    return jsonify({'status': 'success'})



@campaign.route("/<int:campaign_id>/update/")
def update(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).one()
    return render_template("campaign/index.html",model=campaign)

@campaign.route('/campaign/static/css/<path:file_name>')
def css(file_name):
	return send_from_directory('app/static/campaign/stylesheets/', file_name)

@campaign.route('/campaign/static/js/<path:file_name>')
def js(file_name):
	return send_from_directory('app/static/campaign/javascripts', file_name)

@campaign.route('/campaign/static/images/<path:file_name>')
def img(file_name):
	return send_from_directory('app/static/campaign/images', file_name)

@campaign.route('/images/<path:file_name>')
def img2(file_name):
	return send_from_directory('app/static/campaign/images', file_name)

@campaign.route('/campaign/static/fonts/<path:file_name>')
def font(file_name):
	return send_from_directory('app/static/campaign/fonts', file_name)
#------------------ AJAX API -----------------------------------------
from .api import *
comments_func = CommentView.as_view('comments')
campaign.add_url_rule('/comment', view_func=comments_func, defaults={'campaign_id': None}, methods=['POST', 'PUT',
                                                                                                    'DELETE'])
campaign.add_url_rule('/comment/<int:campaign_id>', view_func=comments_func, methods=['GET','POST',
                                                                                                    'PUT', 'DELETE'])