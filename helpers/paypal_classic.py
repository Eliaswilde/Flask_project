import json
import urllib
import urlparse
import collections
import httplib
from config import PAYPAL_SECURITY_USERID, PAYPAL_SECURITY_PASSWORD, PAYPAL_SECURITY_SIGNATURE, PAYPAL_APPLICATION_ID, PAYPAL_PRIMARY_ACCOUNT_EMAIL


def get_header():
    return  {
        'X-PAYPAL-SECURITY-USERID': PAYPAL_SECURITY_USERID,
        'X-PAYPAL-SECURITY-PASSWORD': PAYPAL_SECURITY_PASSWORD,
        'X-PAYPAL-SECURITY-SIGNATURE': PAYPAL_SECURITY_SIGNATURE,
        'X-PAYPAL-APPLICATION-ID': PAYPAL_APPLICATION_ID,
        'X-PAYPAL-SERVICE-VERSION':'1.1.0',
        'X-PAYPAL-REQUEST-DATA-FORMAT':'NV',
        'X-PAYPAL-RESPONSE-DATA-FORMAT':'JSON'
    }


def VerifyPayyment(payKey):
    headers = get_header()

    params = collections.OrderedDict()
    params['requestEnvelope.errorLanguage'] = 'en_US'
    params['payKey'] = str(payKey)

    enc_params = urllib.urlencode(params)
    print ("*****************")
    print (enc_params)
    print ("*****************")

    #Connect to sand box and POST.
    conn = httplib.HTTPSConnection("svcs.sandbox.paypal.com")
    conn.request("POST", "/AdaptivePayments/PaymentDetails/", enc_params, headers)

    print ("*****************")
    #Check the response - should be 200 OK.
    response = conn.getresponse()
    print (response.status, response.reason)
    print ("*****************")

    #Get the reply and print it out.
    data = json.loads(response.read())
    print (data)
    print ("*****************")
    return data
    #return { 'url' : "https://www.sandbox.paypal.com/webscr?cmd=_ap-payment&paykey=%s" % data['payKey'], 'payKey' : data['payKey'] }

def CreateChainedPayment(total,secondary_email,secondary_total,return_url,cancel_url):
#Set our headers
    headers = get_header()
 
    ###################################################################
    # In the above $headers declaration, the USERID, PASSWORD and 
    # SIGNATURE need to be replaced with your own.
    ################################################################### 
 
    #Set our POST Parameters
    params = collections.OrderedDict()
    params['requestEnvelope.errorLanguage'] = 'en_US'
    params['requestEnvelope.detailLevel'] = 'ReturnAll'
    params['returnUrl'] = str(return_url)
    params['cancelUrl'] = str(cancel_url)
    params['actionType'] = 'PAY'
    params['currencyCode'] = 'USD'
    params['feesPayer'] = 'EACHRECEIVER'
    params['receiverList.receiver(0).email'] = str(secondary_email)
    params['receiverList.receiver(0).amount'] = '%.2f' % total
    params['receiverList.receiver(0).primary'] = 'true'
    params['receiverList.receiver(1).email'] = str(PAYPAL_PRIMARY_ACCOUNT_EMAIL)
    params['receiverList.receiver(1).amount'] = '%.2f' % secondary_total
 
    #Add Client Details
 
    params['clientDetails.ipAddress'] = '127.0.0.1'
    params['clientDetails.deviceId'] = 'mydevice'
    params['clientDetails.applicationId'] = 'PayNvpDemo'
 
 
    enc_params = urllib.urlencode(params)
    print ("*****************")
    print (enc_params)
    print ("*****************")
 
    #Connect to sand box and POST.
    conn = httplib.HTTPSConnection("svcs.sandbox.paypal.com")
    conn.request("POST", "/AdaptivePayments/Pay/", enc_params, headers)
 
    print ("*****************")
    #Check the response - should be 200 OK.
    response = conn.getresponse()
    print (response.status, response.reason)
    print ("*****************")
 
    #Get the reply and print it out.
    data = json.loads(response.read())
    print (data)
    print ("*****************")

    return { 'url' : "https://www.sandbox.paypal.com/webscr?cmd=_ap-payment&paykey=%s" % data['payKey'], 'payKey' : data['payKey'] }
 
