import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import tweepy
from sentiment import get_sentiment
from config import BEARER_TOKEN

st.title("Real-Time Twitter Sentiment Analysis")
tweets_data = []

# Define Streaming Client
class TwitterStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        sentiment = get_sentiment(tweet.text)
        tweets_data.append({"tweet": tweet.text, "sentiment": sentiment})
        st.write(f"**Tweet**: {tweet.text}\n**Sentiment**: {sentiment}")

    def on_error(self, status_code):
        if status_code == 420:
            st.error("Rate limit exceeded.")
            return False

# Start Stream
if st.button("Start Streaming"):
    stream = TwitterStream(BEARER_TOKEN)
    try:
        stream.add_rules(tweepy.StreamRule("#AI OR #MachineLearning"))
    except Exception as e:
        st.warning("Rules may already exist.")
    stream.filter(expansions=["author_id"], tweet_fields=["created_at", "lang"], is_async=True)

# Show DataFrame and Charts
if tweets_data:
    df = pd.DataFrame(tweets_data)
    st.subheader("Tweet Data")
    st.dataframe(df)

    st.subheader("Sentiment Distribution")
    fig1, ax1 = plt.subplots()
    df["sentiment"].value_counts().plot.pie(
        autopct="%1.1f%%", colors=["green", "red", "blue"], startangle=90, ax=ax1
    )
    ax1.set_ylabel("")
    st.pyplot(fig1)

    st.subheader("Word Cloud")
    text = " ".join(tweet for tweet in df["tweet"])
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.imshow(wordcloud, interpolation="bilinear")
    ax2.axis("off")
    st.pyplot(fig2)
