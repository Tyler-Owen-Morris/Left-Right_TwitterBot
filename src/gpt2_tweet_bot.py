# ********* MUST BE RUN FROM VIRTUAL ENV WITH TF 1.13.1 INSTALLED W/ GPT-2-SIMPLE ****
# ********* WILL NOT FUNCTION WITH TENSORFLOW GREATER THAN 1.13.1 *****
from tweepy import OAuthHandler, Cursor, API
import json
import pandas as pd
import time
from random import randint, randrange, choice
import gpt_2_simple as gpt2

import twitter_credentials_left as tc

auth = OAuthHandler(tc.CONSUMER_KEY, tc.CONSUMER_SECRET)
auth.set_access_token(tc.ACCESS_TOKEN, tc.ACCESS_TOKEN_SECRET)
api = API(auth, wait_on_rate_limit=True)
print('twitter logged in...')

def generate_generic_tweet(session):
    print('generating generic tweets...')
    gpt2.generate_to_file(session, destination_path='../data/generated_tweets.txt', run_name='run2')
    print("tweet generation complete...")
    with open('../data/generated_tweets.txt', 'r', encoding='utf-8') as in_file:
        tweets = in_file.read().split(' || ')
    print('tweets split, beginning filter...')
    tweet = choose_and_clean_tweet(tweets)
    #print(tweet)
    return tweet

def generate_trending_tweet(session):
    trending = get_trending()
    topic = choice(trending)
    print("generating topical tweets on subject: "+ topic)
    gpt2.generate_to_file(session, destination_path='../data/generated_tweets.txt', nsamples=5, run_name='run2', prefix=topic)
    print("topical tweet generation complete...")
    with open('../data/generated_tweets.txt', 'r', encoding='utf-8') as in_file:
        tweets = in_file.read().split(' || ')
    tweet = tweets[0]
    if len(tweet) > 280:
        tweet = tweet[:280]
    return tweet

def choose_and_clean_tweet(tweets):
    idx = randrange(0,len(tweets))
    tweet = tweets.pop(idx).split(" ")
    tweet = " ".join(word for word in tweet if not has_prefix(word))
    print("before shortening"+tweet)
    if len(tweet) > 280:
        tweet = tweet[:280]
    print("after shortening: "+tweet)
    return tweet

def get_trending():
    trends = api.trends_place(id=23424977) #this is the code for USA
    trending =[]
    for trend in trends[0]['trends']:
        trending.append(trend['name'])
        #print(trend['name'])
    return trending

def has_prefix(word):
    for x in ['@', 'http']:
        if word.find(x) != -1:
            return True
    return False

def do_bot_things():
    session = gpt2.start_tf_sess()
    gpt2.load_gpt2(session, run_name='run2')
    print('session started...')
    while True:
        roll = randint(0,10)
        if roll < 7:
            tweet = generate_trending_tweet(session)
        else:
            tweet = generate_generic_tweet(session)
        print("I would be tweeting : "+tweet)
        #api.update_status(tweet)

        sleep_time = (11*60) + randint(-10,3)*60
        print("Going to sleep for "+str(sleep_time/60)+" minutes")
        time.sleep(sleep_time)

if __name__ == "__main__":
    do_bot_things()