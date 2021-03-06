import sys
import os
import requests
import logging
import json
import uuid
from datetime import datetime, timedelta
from flask_restful import reqparse, abort, Api, Resource
from flask import request
from flask import jsonify, make_response, redirect, render_template, url_for
from flask import Blueprint

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from settings import *

transaction = Blueprint('transaction', __name__)
logging.basicConfig(stream=sys.stderr)
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger()


@transaction.route("/", methods=['GET'])
def home():
    token = request.cookies.get('Access-Token')

    if token == None:
        return redirect(LOGIN_PAGE_URL, code=302)

    # ---validate user---
    valid_user(token)

    # ---get user mail---
    headers = {"Access-Token": token, "API-Token": IAM_CLIENT_SECRET}
    response = requests.get(IAM_USER, headers=headers)

    if response.status_code != 200:
        return redirect(LOGIN_PAGE_URL, code=302)

    user = response.json()['data']['email']
    name = response.json()['data']['name']
    image = response.json()['data']['picture_url']

    return render_template('transaction.html', user=user, image=image, name=name)


@transaction.route("/new", methods=['POST'])
def new_transaction():
    token = request.cookies.get('Access-Token')
    price = request.form['price']
    seller_email = request.form['seller_email']
    description = request.form['description']
    url = request.form['url']

    if token == None:
        return redirect(LOGIN_PAGE_URL, code=302)

    # ---validate user---
    valid_user(token)

    # ---get user id---
    headers = {"Access-Token": token, "API-Token": IAM_CLIENT_SECRET}
    response = requests.get(IAM_USER, headers=headers)

    if response.status_code != 200:
        return redirect(LOGIN_PAGE_URL, code=302)

    user_id = response.json()['data']['uid']

    # ---get seller id---
    # headers = {"Access-Token": token} FALAR COM O BRUNO
    headers = {"API-Token": IAM_CLIENT_SECRET}
    response = requests.get(IAM_USER + "?email=" + seller_email, headers=headers)

    if response.status_code != 200:
        return "Email not found", 400

    seller_id = json.loads(response.text)['data']['uid']
    # response.json()['data']['uid']

    # ---create object---
    data = {'name': description,
            'url': url,
            'identifier': user_id
            }
    response = requests.post(TRANSACTIONS_NEW_OBJECT, data=data)

    if response.status_code == 400:
        return "Error creating object", 400

    info = response.json()
    object_uuid = info["id"]

    # ---create transaction---

    data = {'to_uuid': seller_id,
            'from_uuid': user_id,
            'object_uuid': object_uuid,
            'price': price,
            'state': "AWAITING_CONFIRMATION"}

    response = requests.post(TRANSACTIONS_NEW, data=data)
    info = response.json()

    if response.status_code != 201:
        return "Error creating transaction", 400

    resp = requests.get(TRANSACTIONS_DETAILS.format(info['id']))
    if resp.status_code != 200:
        return "ID not found", 400
    info = resp.json()

    headers = {"API-Token": IAM_CLIENT_SECRET}
    resp = requests.get(IAM_USER + "?id=" + info['to_uuid'], headers=headers)
    if resp.status_code != 200:
        return "ID not found", 400
    to_email = json.loads(resp.text)['data']['email']

    data = {'email': to_email,
            'message': 'There is a new transaction waiting confirmation for this item:' + info['object']['url']}

    response = requests.post(NOTIFICATION_EMAIL, data=data)

    response = redirect(TRANSACTIONS_URL, code=302)
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response


@transaction.route("/list", methods=['GET'])
def list_transactions():
    dataType = request.args.get('dataType')
    token = request.cookies.get('Access-Token')

    if token == None:
        return redirect(LOGIN_PAGE_URL, code=302)

    # ---validate user---
    valid_user(token)

    # ---get user id---
    headers = {"Access-Token": token, "API-Token": IAM_CLIENT_SECRET}
    response = requests.get(IAM_USER, headers=headers)

    if response.status_code != 200:
        return redirect(LOGIN_PAGE_URL, code=302)

    user_id = response.json()['data']['uid']

    # ---get transaction list---
    response = requests.get(TRANSACTIONS_LIST.format(user_id))
    info = response.json()

    if response.status_code != 200:
        return "Error retrieving transactions list", 400

    response = []
    if dataType == "seller":
        for trans in info['to_uuid']:

            headers = {"API-Token": IAM_CLIENT_SECRET}
            resp = requests.get(IAM_USER + "?id=" + trans['from_uuid'], headers=headers)
            if resp.status_code != 200:
                return "ID not found", 400

            if trans['state'] == 'SHIPPED' and trans['tracking_code'] == "":
                tracking = "<a href=\"/tracking?id=" + trans['id'] + "\" class=\"btn btn-info\">Add Tracking N.</a>"

            elif trans['tracking_code'] == "":
                tracking = "None"

            else:

                tracking = "<a href=\"https://pkt-tracker.ddns.net/search.php?track=&tracking_nr=" + trans[
                    'tracking_code'] + "&carrier=CTT\"><span class=\"badge\">" + trans['tracking_code'] + "</span></a><br>"
            address = json.loads(resp.text)['data']['address'].encode("utf-8")
            response.append({'state': transformState(trans['state']),
                             'buyer': json.loads(resp.text)['data']['email'],
                             'price': trans['price'],
                             'url': trans['object']['url'],
                             'tracking': tracking,
                             'actions': action(dataType, trans['state'], trans['id'], address)
                             })
    elif dataType == "buyer":
        for trans in info['from_uuid']:

            headers = {"API-Token": IAM_CLIENT_SECRET}
            resp = requests.get(IAM_USER + "?id=" + trans['to_uuid'], headers=headers)
            if resp.status_code != 200:
                return "ID not found", 400
            if trans['tracking_code'] == "":
                tracking = "None"
            else:
                tracking = "<a href=\"https://pkt-tracker.ddns.net/search.php?track=&tracking_nr=" + trans[
                    'tracking_code'] + "&carrier=CTT\"><span class=\"badge\">" + trans['tracking_code'] + "</span></a><br>"
            response.append({'state': transformState(trans['state']),
                             'seller': json.loads(resp.text)['data']['email'],
                             'price': trans['price'],
                             'url': trans['object']['url'],
                             'tracking': tracking,
                             'actions': action(dataType, trans['state'], trans['id'])
                             })

    elif dataType == "rating":

        for trans in info['from_uuid']:
            headers = {"API-Token": IAM_CLIENT_SECRET}
            resp = requests.get(IAM_USER + "?id=" + trans['to_uuid'], headers=headers)
            if resp.status_code != 200:
                return "ID not found", 400

            if (trans['state'] == "COMPLETED") or (trans['state'] == "REFUND"):
                resp_rate = requests.get(RATING_TRANSACTIONS + trans['id'])
                if resp_rate.status_code != 200:

                    response.append({'state': transformState(trans['state']),
                                 'seller': json.loads(resp.text)['data']['email'],
                                 'url': trans['object']['url'],
                                 'rate': "<a href=\"/rating/review?id=" + trans['id'] + " \" class=\"btn btn-primary\">Add Review</a>"
                                 })

    return jsonify(response)


def valid_user(token):
    # ---validate user---
    headers = {"Access-Token": token, "API-Token": IAM_CLIENT_SECRET}
    response = requests.post(IAM_VALIDATE, headers=headers)

    if response.status_code != 200:
        return redirect(LOGIN_PAGE_URL, code=302)


def transformState(state):
    if state == "AWAITING_CONFIRMATION":
        return "<span class=\"label label-primary\">Awaiting Confirmation</span>"
    elif state == "AWAITING_PAYMENT":
        return "<span class=\"label label-primary\">Awaiting Payment</span>"
    elif state == "AWAITING_SHIPPING":
        return "<span class=\"label label-primary\">Awaiting Shipment</span>"
    elif state == "SHIPPED":
        return "<span class=\"label label-warning\">Shiped</span>"
    elif state == "COMPLETED":
        return "<span class=\"label label-success\">Success</span>"
    elif state == "REFUND":
        return "<span class=\"label label-danger\">Refund</span>"


def action(dataType, state, id, address=""):
    if dataType == "buyer":
        if state == "AWAITING_PAYMENT":
            return "<a onClick=\"pay('" + id + "')\" class=\"btn btn-success\">Pay</a>"
        elif state == "SHIPPED":
            return "<a href=\"/pay_gateway/complete?id=" + id + "\" class=\"btn btn-primary\">Received</a>" + "<a href=\"/pay_gateway/refund?id=" + id + "\" class=\"btn btn-warning\">Refund</a>"
        else:
            return "None"
    elif dataType == "seller":
        if state == "AWAITING_CONFIRMATION":
            return "<a href=\"/change_state?id=" + id + "&state=AWAITING_PAYMENT\" class=\"btn btn-primary\">Confirm</a>"
        elif state == "AWAITING_SHIPPING":

            return "<button type=\"button\" class=\"btn btn-warning btn-xs\" data-toggle=\"modal\" data-target=\"#myModal\">See Address</button> \
            <!-- Modal --> \
            <div class=\"modal fade\" id=\"myModal\" role=\"dialog\"> \
            <div class=\"modal-dialog\"> \
            <!-- Modal content--> \
            <div class=\"modal-content\"> \
            <div class=\"modal-header\"> \
            <button type=\"button\" class=\"close\" data-dismiss=\"modal\">&times;</button> \
            <h4 class=\"modal-title\">Buyer Address</h4> \
            </div> \
            <div class=\"modal-body\"> \
            <p>" + address.decode("utf-8") + "</p> \
            </div> \
            <div class=\"modal-footer\"> \
            <button type=\"button\" class=\"btn btn-default\" data-dismiss=\"modal\">Close</button> \
            </div> \
            </div> \
            </div> \
            </div>" + "<a href=\"/change_state?id=" + id + "&state=SHIPPED\" class=\"btn btn-primary btn-sm\">Sent</a>"
        else:
            return "None"
