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

def update_counter():
    r.set("counter", ((int(r.get("counter")) + 1)% 24))

def get_tweet():
    boring_phrase = make_plain_post()
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a twitter bot that displays daily sales reports of website domains."},
            {"role": "user", "content": f"Here's a boring tweet: {boring_phrase}. Rewrite this to make it an exciting tweet and add emojis (encoded in utf-8) too."}
        ],
        max_tokens=100,
        temperature=0.8
    )
    return completion.choices[0].message.content


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
    # Initialize an empty string to store the formatted output
    records_output_string = ""

    domain = "https://" + record['Domain']
    price = "${:,}".format(int(record['Price']))
    venue = record['Venue']
    record_output_string = f"{domain} sold for {price} at {venue}\n"
    return record_output_string


def fetch_database_record():
    database_record = r.lindex('records_data', int(r.get("counter")))
    # Decode JSON strings back to dictionaries
    decoded_database_record = json.loads(database_record)
    update_counter()
    return decoded_database_record


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
