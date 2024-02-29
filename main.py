import base64
import hashlib
import os
import re
import json
import requests
import redis
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth2Session, TokenUpdated
from flask import Flask, request, redirect, session, url_for, render_template
from openai import OpenAI

r = redis.from_url(os.environ["REDIS_URL"])


def get_tweet():
    return make_plain_post()


def get_day_tweet():
    return make_day_post()


def get_headline():
    return make_headline_post()


app = Flask(__name__)
app.secret_key = os.urandom(50)

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
auth_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
redirect_uri = os.environ.get("REDIRECT_URI")

scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]

code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")


def make_token():
    return OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)


def make_plain_post():
    record = fetch_database_record()
    domain = "https://" + record['Domain']
    price = "${:,}".format(int(record['Price']))
    venue = record['Venue']
    record_output_string = f"Domain name {domain} sold for {price} on {venue} "
    record_output_string = record_output_string + "\U0001F38A" + " #Domains"
    return record_output_string


def make_headline_post():
    headline = fetch_headline()
    title = headline['title']
    link = headline['link']
    return f"\U0001F4F0 {title}\n{link}" + " #Domains"


def make_day_post():
    sales = r.get('sales')
    sales = str(sales, encoding='utf-8')
    sales = int(sales)
    r.set('flag', "False")
    return "Yesterday's domain sales from all marketplaces totaled " + f"${sales:,} " + "\U0001F911" + "#Domains"


def fetch_database_record():
    raw_stack = r.get('stack')
    output_stack = json.loads(raw_stack)
    decoded_database_record = output_stack.pop()
    input_stack = json.dumps(output_stack)
    r.set('stack', input_stack)
    return decoded_database_record


def fetch_headline():
    headlines = r.get('headlines')
    output_stack = json.loads(headlines)
    output_headline = output_stack.pop()
    input_stack = json.dumps(output_stack)
    r.set('headlines', input_stack)
    return output_headline


def post_tweet(payload, token):
    print("Tweeting!")
    return requests.request(
        "POST",
        "https://api.twitter.com/2/tweets",
        json=payload,
        headers={
            "Authorization": "Bearer {}".format(token["access_token"]),
            "Content-Type": "application/json",
        },
    )


@app.route("/")
def demo():
    global x
    x = make_token()
    authorization_url, state = x.authorization_url(
        auth_url, code_challenge=code_challenge, code_challenge_method="S256"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)


@app.route("/oauth/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    token = x.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        code_verifier=code_verifier,
        code=code,
    )
    st_token = '"{}"'.format(token)
    j_token = json.loads(st_token)
    r.set("token", j_token)
    content = get_tweet()
    payload = {"text": "{}".format(content)}
    response = post_tweet(payload, token).json()
    return response


if __name__ == "__main__":
    app.run()
