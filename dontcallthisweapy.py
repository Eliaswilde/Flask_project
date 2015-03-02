from wepay import WePay

# application settings
account_id = 1178716227
access_token = 'STAGE_91d23ae0d1b8ed89e4d5585137748aad7c0e1ff58ea725b16455af78bd3b8ca5'
production = False

# credit card id to charge
credit_card_id = 2207927703

# set production to True for live environments
wepay = WePay(production, access_token)

# charge the credit card
response = wepay.call('/checkout/create', {
	'account_id': account_id,
	'amount': '25.50',
	'short_description': 'A brand new soccer ball',
	'type': 'GOODS',
	'payment_method_id': credit_card_id, # the user's credit_card_id
	'payment_method_type': 'credit_card'
})

# display the response
print response