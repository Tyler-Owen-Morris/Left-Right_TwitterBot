# ********* MUST BE RUN FROM VIRTUAL ENV WITH TF 1.13.1 INSTALLED W/ GPT-2-SIMPLE ****
# ********* WILL NOT FUNCTION WITH TENSORFLOW GREATER THAN 1.13.1 ********************
from tweepy import OAuthHandler, Cursor, API
import json
import pandas as pd
import time
import os
from random import randint, randrange, choice
import gpt_2_simple as gpt2

import twitter_credentials_biden as tc

auth = OAuthHandler(tc.CONSUMER_KEY, tc.CONSUMER_SECRET)
auth.set_access_token(tc.ACCESS_TOKEN, tc.ACCESS_TOKEN_SECRET)
api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
print('twitter logged in...')
model_name = "355M"
if not os.path.isdir(os.path.join("models", model_name)):
    print(f"Downloading {model_name} model...")
    gpt2.download_gpt2(model_name=model_name)
print("model loaded")


def generate_trending_tweet():
    topics = ["Biden", "Trump"]
    topic = choice(topics)
    # this is just for testing repeat topics- remove before deployment
    print("generating topical tweets on subject: " + topic)

    # update the text file with current tweets
    file_name = '../data/'+topic+'.txt'
    topical_tweets = get_topic_tweets(topic, 2500)
    t_tweet_string = " || ".join(topical_tweets)

    with open(file_name, 'w') as f:
        f.write(t_tweet_string)

    # train model
    print("training new model on scraped text for topic : "+topic)
    sess = gpt2.start_tf_sess()

    if not os.path.exists('checkpoint/'+topic):
        # train fresh model
        print("training fresh model- none found...")
        gpt2.finetune(sess,
                      dataset=file_name,
                      model_name=model_name,
                      steps=200,
                      restore_from='fresh',
                      run_name=topic,
                      print_every=1)
    else:
        # update existing model
        print("updating existing model with short run on new tweets...")
        gpt2.finetune(sess,
                      dataset=file_name,
                      model_name=model_name,
                      run_name=topic,
                      steps=100,
                      restore_from='latest',
                      print_every=1)
    # generate tweet
    print("beginning to generate tweets...")
    gpt2.generate_to_file(sess,
                          length=400,
                          destination_path='../data/generated_tweets.txt',
                          nsamples=10,
                          run_name=topic,
                          prefix=topic)
    print('done generating tweets... ')
    # reset the session to prevent errors on loop
    gpt2.reset_session(sess=sess)
    # return 1 tweet
    with open('../data/generated_tweets.txt', 'r') as f:
        texts = f.read().split('====================')
    tweets = []
    for text in texts:
        # by just taking the first tweet, we're sure we have the seed text
        tweeters = text.split(' || ')
        for tweet in tweeters:
            if topic in tweet:  # ensure it contains the topic string
                tweet = tweet.split(" ")
                # remove links
                tweet = " ".join(
                    word for word in tweet if not has_prefix(word))
                # ensure it's not just the topic word only
                if len(tweet) > len(topic)+4 & len(tweet) <= 280:
                    tweets.append(tweet)
            else:
                continue
    #print("Potential tweets:\n"+ " \n\n ".join(tweets))
    tweet = choice(tweets)
    if len(tweet) > 280:
        tweet = tweet[:280]
    return tweet


def get_trending():
    trends = api.trends_place(id=23424977)  # this is the code for USA
    trending = []
    for trend in trends[0]['trends']:
        trending.append(trend['name'])
        # print(trend['name'])
    return trending


def get_topic_tweets(topic, max_tweets=100):
    if topic == "Trump":
        sentiment = " :("
    else:
        sentiment = " :)"
    query = topic + sentiment
    print("using twitter api query: " + query)
    searched_tweets = [status for status in Cursor(
        api.search, q=query, lang='en', tweet_mode='extended').items(max_tweets)]
    found_tweets = []
    for tweet in searched_tweets:
        try:
            found_tweets.append(tweet.full_text)
        except:
            print("failed to get full text for this tweet...")
    return found_tweets


def has_prefix(word):
    for x in ['http']:
        if word.find(x) != -1:
            return True
    return False


def run_bot():

    while True:
        tweet = generate_trending_tweet()
        print("I am tweeting : "+tweet)
        api.update_status(tweet)
    print("exited loop somehow...")


if __name__ == "__main__":
    run_bot()
