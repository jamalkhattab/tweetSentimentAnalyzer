import csv
import tweepy
import nltk
import os
import re
from nltk.corpus import stopwords
from textblob import TextBlob
from azure.storage.blob import BlobServiceClient

def cleanTweet(original_tweet):
    # Load the English stopwords in NLTK
    stop_words = set(stopwords.words('english'))
    
    # Remove the stop words from the tweet
    tweet = " ".join([word for word in original_tweet.split() if word.lower() not in stop_words])

    # Remove URLs
    tweet = re.sub(r"http\S+", "", tweet)

    # Remove emojis and other unwanted characters
    tweet = re.sub(r'[^\w\s#@/:%.,_-]', '', tweet)
    return tweet

def pushCsvToAzureBlob():
    # Define the connection string and container name
    connect_str = "<REPLACE_WITH_CONNECTION_STRING>"
    container_name = "<REPLACE_WITH_CONTAINER_NAME>"

    # Define the local CSV file path and name
    local_file_path = "azure_tweets_sentiment.csv"

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Get a ContainerClient object
    container_client = blob_service_client.get_container_client(container_name)

    # Define the name for the Blob
    blob_name = os.path.basename(local_file_path)

    # Get a BlobClient object for the Blob
    blob_client = container_client.get_blob_client(blob_name)

    # Upload the CSV file to the Blob
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print("Uploading CSV to BlobStorageAccount complete.")    

def collectTweets(topic):
    # Set up your Twitter API credentials
    consumer_key = "<REPLACE_WITH_CONSUMER_KEY>"
    consumer_secret = "<REPLACE_WITH_CONSUMER_SECRET>"
    access_token = "<REPLACE_WITH_ACCESS_TOKEN>"
    access_token_secret = "<REPLACE_WITH_ACCESS_TOKEN_SECRET>"

    # Authenticate with the Twitter API using Tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Create the API object
    api = tweepy.API(auth)
    
    #Grab 100 tweets with the requested topic
    tweets = []
    for tweet in tweepy.Cursor(api.search_tweets, q=topic, tweet_mode='extended').items(100):
        if "retweeted_status" in dir(tweet):
            tweets.append(tweet.retweeted_status.full_text)
        else:
            tweets.append(tweet.full_text)
    print("Finished grabbing %d tweets about %s." % (len(tweets),topic))        
    return tweets        


if __name__ == "__main__":
    # Download the stopwords if necessary
    nltk.download('stopwords')

    # Search for tweets about Microsoft Azure
    tweets = collectTweets("Microsoft Azure")

    # Define the sentiment analyzer
    sia = lambda text: TextBlob(text).sentiment.polarity

    # Open a CSV file to store the retrieved tweets and sentiment scores
    with open('azure_tweets_sentiment.csv', mode='w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(['Tweet', 'Sentiment'])
        
        print("Perfoming Sentiment Analysis on the tweets.")
        # Analyze the sentiment of each tweet and write it to the CSV file
        for tweet in tweets:
            clean_tweet = cleanTweet(tweet)

            # Analyze the sentiment of the filtered tweet
            sentiment = sia(clean_tweet)

            # Write the tweet and sentiment score to the CSV file
            writer.writerow([clean_tweet, sentiment])
            
    pushCsvToAzureBlob()





