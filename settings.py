import os
import requests

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

ALLOWED_HOSTS="0.0.0.0"
PORT = 80

__APP_NAME__ = "TranSafe"

HOST = "localhost"

IAM_USER = "https://im.transafe.rafaelferreira.pt/user"
IAM_USER_DATA = "https://im.transafe.rafaelferreira.pt/user/add_user_data"
IAM_VALIDATE = "https://im.transafe.rafaelferreira.pt/validate"
IAM_SIGNUP = "https://im.transafe.rafaelferreira.pt/login"
IAM_LOGOUT = "https://im.transafe.rafaelferreira.pt/logout"
IAM_USERS_COUNT = "https://im.transafe.rafaelferreira.pt/user/count"

PAY_SERVICE_TOKEN_ID = "396428be-8bc7-415e-81d4-bbf698ab9d64"
PAY_SERVICE_MYCARDS = "https://payments.transafe.rafaelferreira.pt/api/v1/cards/mycards/"
PAY_SERVICE_CREATE_CARD = "https://payments.transafe.rafaelferreira.pt/api/v1/cards/create/"
PAY_SERVICE_CREATE_PAYMENT = "https://payments.transafe.rafaelferreira.pt/api/v1/payments/create/"
PAY_SERVICE_COMPLETE_PAYMENT = "https://payments.transafe.rafaelferreira.pt/api/v1/payments/complete/"
PAY_SERVICE_REFUND_PAYMENT = "https://payments.transafe.rafaelferreira.pt/api/v1/payments/refund/"
__TRANSACTIONS_TOKEN__ = None


def transactions_token():
    global __TRANSACTIONS_TOKEN__

    if __TRANSACTIONS_TOKEN__ is None:
        r = requests.post('http://10.0.11.12/api/v1/register/app/', data={'name': __APP_NAME__})
        # r = requests.post('http://10.0.11.12/api/v1/register/app/', data={'name': "flask"})
        __TRANSACTIONS_TOKEN__ = r.json()["token"]
        return __TRANSACTIONS_TOKEN__
    else:
        return __TRANSACTIONS_TOKEN__

__TRANSACTIONS_BASE__ = "http://10.0.11.12/api/v1/"
TRANSACTIONS_NEW = (__TRANSACTIONS_BASE__ + "transaction/new/?token=%s" % transactions_token())
TRANSACTIONS_NEW_OBJECT = (__TRANSACTIONS_BASE__ + "object/new/?token=%s" % transactions_token())
TRANSACTIONS_UPDATE = (__TRANSACTIONS_BASE__ + "transaction/state/?token=%s" % transactions_token())
TRANSACTIONS_LIST = (__TRANSACTIONS_BASE__ + "transaction/history/{0}/?token=%s" % transactions_token())
TRANSACTIONS_DETAILS = (__TRANSACTIONS_BASE__ + "transaction/details/{0}/?token=%s" % transactions_token())
TRANSACTIONS_TRACKING = (__TRANSACTIONS_BASE__ + "transaction/tracking_code/?token=%s" % transactions_token())
TRANSACTIONS_STATS = (__TRANSACTIONS_BASE__ + "transaction/stats/?token=%s" % transactions_token())

AUTH_CALLBACK_URL = "https://transafe.rafaelferreira.pt/authorize/signup_callback"
TRANSACTIONS_URL = "https://transafe.rafaelferreira.pt/transaction"
LOGIN_PAGE_URL = "https://transafe.rafaelferreira.pt/"
DASHBOARD_URL = "https://transafe.rafaelferreira.pt/dashboard"
PAY_GATEWAY_URL = "https://transafe.rafaelferreira.pt/pay_gateway"
PAY_GATEWAY_CALLBACK_URL = "https://transafe.rafaelferreira.pt/pay_gateway/callback"
CHANGE_STATE_URL = "https://transafe.rafaelferreira.pt/pay_gateway/change_state"
PAY_GATEWAY_CONFIRMED_URL = "https://transafe.rafaelferreira.pt/pay_gateway/payment_success"

NOTIFICATION_EMAIL = "http://10.0.11.14/api/v1/notification/email/"
NOTIFICATION_MESSENGER = "http://10.0.11.14/api/v1/notification/messenger/"

RATING_RATE = "http://10.0.11.16/api/v1/rating/"
RATING_TRANSACTIONS = "http://10.0.11.16/api/v1/rating/transaction/"
RATING = "http://10.0.11.16/api/v1/rate/"

PAYPAL_CLIENT_ID = "AW3iw3rOWtZt_VrhggnaNYl1_7FJ6lAf04SwAXAFfHmVUAkXX6bz55pSBnemeJ3z-Vytymv1FP7mVWBt"
PAYPAL_CLIENT_SECRET = "ENqKPCSabqwaDsLKncTGjeXDLlYyIEALMg9yiRdZG8BS7TvqLPINd303YhMvmLCJptEeRRHhUSS0JM6T"

IAM_CLIENT_ID = "2c599753-fc9e-40c8-9a1b-ab76fb7bf812"
IAM_CLIENT_SECRET = "I7RSTP4ZG2MZK2ZDOGJQW4ATMHPZJ2SPYIJQUHZJG6QBJ4KCQFUDESL2Z55LPTJSSZBC6BV3KOBU3SL24LLUBJUI6JN45AZBONUOLUVFVUZCVOXJKBEU6TBIUADCFTJLVGL4X5A3M6NNHJM4Q2S3I4XPX2BB2VIQ"
