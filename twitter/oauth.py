#!/usr/bin/env python
import tweepy
import os

"""
Script to generate token to allow twitter dev account to 
use API as another twitter account.

Require tweepy dependency
Use for airbyte connector 
"""

def print_help():
    print("The variables CLIENT_ID, CLIENT_SECRET and REDIRECT_URI must be set")
    print("The CLIENT_ID and CLIENT_SECRET are generated when creating a twitter App : https://developer.twitter.com/en/portal/projects-and-apps")
    print("The REDIRECT_URI is set throught the User Authentication settings in the twitter app and must be in https")

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
    client_id= os.environ.get("CLIENT_ID"),
    redirect_uri=os.environ.get("REDIRECT_URI"),
    scope=["tweet.read", "users.read", "tweet.write", "offline.access"],
    client_secret=os.environ.get("CLIENT_SECRET")
)

print("Copy this url in a browser logged in the Twitter account.")
print(oauth2_user_handler.get_authorization_url())

authorization_response_url=input("Enter the authorization response URL. ")

print("URL : %s" % authorization_response_url)

access_token = oauth2_user_handler.fetch_token(
    authorization_response_url
)

print("Access token : %s" % access_token)
