#!/usr/bin/env python
import tweepy
import os
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

"""
Script to generate token to allow twitter dev account to
use API as another twitter account.

Require tweepy dependency
Use for airbyte connector
"""

def print_help():
    logger.info("The variables CLIENT_ID, CLIENT_SECRET and REDIRECT_URI must be set")
    logger.info("The CLIENT_ID and CLIENT_SECRET are generated when creating a twitter App : https://developer.twitter.com/en/portal/projects-and-apps")
    logger.info("The REDIRECT_URI is set throught the User Authentication settings in the twitter app and must be in https")

if "CLIENT_ID" not in os.environ:
    print_help()
    exit(1)
if "CLIENT_SECRET" not in os.environ:
    print_help()
    exit(1)
if "REDIRECT_URI" not in os.environ:
    print_help()
    exit(1)

oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id=os.environ.get("CLIENT_ID"),
    redirect_uri=os.environ.get("REDIRECT_URI"),
    scope=[
        "tweet.read",
        "users.read",
        "space.read",
        "offline.access"
    ],
    client_secret=os.environ.get("CLIENT_SECRET")
)

print(oauth2_user_handler.get_authorization_url())
authed = False
while not authed:
    try:
        authorization_response_url=input("Enter the authorization response URL. ")
        logger.info("URL : %s", authorization_response_url)
        access_token = oauth2_user_handler.fetch_token(
            authorization_response_url
        )
        authed = True
    except Exception as e:
        logger.error("Something weird happend, please restart %s", e)

logger.info("Access token : %s", access_token)
headers={"Authorization": f"Bearer {access_token.get('access_token')}"}
logger.info("Header %s", headers)

resp = requests.get("https://api.x.com/2/users/me", headers=headers)

logger.info("User infos : %s", resp.json().get("data"))
