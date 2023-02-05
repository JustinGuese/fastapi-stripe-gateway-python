import os
from os import environ

import stripe
from fastapi import Cookie, FastAPI, Request
from fastapi.responses import RedirectResponse
from requests import get

app = FastAPI(title="Payment Gateway Stripe", version="0.1.0")

# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys

stripe.api_key = environ["STRIPE_API_KEY"]

stripe.billing_portal.Configuration.create(
  business_profile={
    "headline": "Pseudonymisieren.de Payment Gateway",
  },
  features={"invoice_history": {"enabled": True}},
)

BASE_URL = "https://payment.datafortress.cloud"

def getUserInfo(cookie: str):
    assert len(cookie) > 1
    cookies = {'_oauth2_proxy': cookie}
    # TODO: change to prod
    try:
        resp = get(BASE_URL + "/oauth2/userinfo", cookies = cookies)
        resp = resp.json()
    except:
        resp = dict()
        resp["email"] = ""
    return resp
    
def checkIfCustomerExists(email: str):
    resp = stripe.Customer.search(
        query="email:'%s'" % email,
    )
    if len(resp["data"]) == 0:
        return None
    else:
        return resp["data"][0]["id"]

@app.get('/create-customer-portal-session', tags=["Payment Gateway"])
def customer_portal( _oauth2_proxy: str = Cookie(default="")):
    # Authenticate your user.
    print("oauthproxy is: ", _oauth2_proxy)
    userinfo = getUserInfo(_oauth2_proxy)
    print("userinfo is: ", userinfo)
    # userinfo is:  {'user': '397e8e5a-fe6e-4af3-8cd5-cbf77400efe9', 'email': 'guese.justin@gmail.com'}                   
    customer = checkIfCustomerExists(userinfo["email"])
    if customer is None:
        print("customer does not exist, create: ", userinfo["email"])
        customer = stripe.Customer.create(
            email=userinfo["email"],
            description="Customer for " + userinfo["email"],
            metadata={"id": userinfo["user"]},
        )
    
    session = stripe.billing_portal.Session.create(
        customer=customer["id"],
        return_url=BASE_URL + '/account',
    )
    return RedirectResponse(session.url)

@app.get("/pseudode/subscription/{stripeproductid}", tags=["Payment Gateway"])
def getSubscription(stripeproductid: str, _oauth2_proxy: str = Cookie(default="")):
    userinfo = getUserInfo(_oauth2_proxy)
    customer = checkIfCustomerExists(userinfo["email"])
    if customer is None:
        print("customer does not exist, create: ", userinfo["email"])
        customer = stripe.Customer.create(
            email=userinfo["email"],
            description="Customer for " + userinfo["email"],
            metadata={"id": userinfo["user"]},
        )
    returnurl = "https://pseudonymisieren.de"
    session = stripe.checkout.Session.create(
        success_url=returnurl + '/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=returnurl + '/canceled',
        mode='subscription',
        customer = customer["id"],
        line_items=[{
            'price': stripeproductid,
            # For metered billing, do not pass quantity
            'quantity': 1
        }],
        )
    return RedirectResponse(session.url)
