# -*- coding: utf-8 -*-
from twitterfunctions import *
import pandas as pd
import os
import time 
from bs4 import BeautifulSoup
import pickle
import re, unicodedata
import nltk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options  
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image
from collections import Counter
from nltk.tokenize import RegexpTokenizer


def Login(browser, username, password):
    
    browser.get("https://twitter.com/login")
    
    username_field = browser.find_element_by_class_name("js-username-field")
    password_field = browser.find_element_by_class_name("js-password-field")
    
    username_field.send_keys(username)
    browser.implicitly_wait(2)
    
    password_field.send_keys(password)
    browser.implicitly_wait(2)
    
    browser.find_element_by_class_name("EdgeButtom--medium").click()

    time.sleep(3)


def Get_posts_links(browser, user_handle, scrolldowns):
    posts = []
    base_url = 'https://twitter.com/'
    url = base_url + user_handle
    browser.get(url)
    time.sleep(1)
    body = browser.find_element_by_tag_name('body')

    htmls = []
    counter = 0
    for _ in range(scrolldowns):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        counter += 1
        if counter % 3 == 0:
            html = browser.page_source
            htmls.append(html)

    for ht in htmls:
        bs = BeautifulSoup(ht, features = 'lxml')
        for x in bs.find_all('a', href = re.compile('(/'+user_handle+'/status/\d+)')):
            if x['href'] not in posts:
                posts.append(x['href'])

    print(posts)
    return posts

def Access_all_likes(link_to_tweet):
    links_to_like = ['https://twitter.com' + x + '/likes' for x in link_to_tweet if 'photo' not in x and 'video' not in x]
    print(links_to_like)
    return links_to_like


def get_likers(browser, link_to_like):
    likers = []
    browser.get(link_to_like)
    time.sleep(5)
    try:
        inn = browser.find_element_by_xpath('//div[@aria-label="Timeline: Liked by"]')
        html_inn = inn.get_attribute('innerHTML')
        sopa = BeautifulSoup(html_inn, features = 'lxml')
        for x in sopa.find_all('a'):
    #print(x)
            if ('search?q=' not in x['href']) and (x['href'] not in [like[1] for like in likers]):
                print(x['href'])
                likers.append((link_to_like[:-6], 'https://twitter.com'+ x['href']))

    except:
        inn = browser.find_elements_by_xpath('//div[@role="button"]')
        sopa = [BeautifulSoup(html.get_attribute('innerHTML'), features = 'lxml') for html in inn]
        for p in sopa:
            for x in p.find_all('a'):
            #print(x)
                if ('search?q=' not in x['href']) and (x['href'] not in [like[1] for like in likers]):
                    print(x['href'])
                    likers.append((link_to_like[:-6], 'https://twitter.com'+ x['href']))

    time.sleep(4)

    return likers


def liker_tweets(browser, liker_handles, scrolldowns):
    tw = []
    browser.get(liker_handles)
    time.sleep(1)
    
    body = browser.find_element_by_tag_name('body')
    
    for _ in range(scrolldowns):
    	body.send_keys(Keys.PAGE_DOWN)
    	time.sleep(0.5)
    
    tweets = browser.find_elements_by_class_name('tweet-text')
    
    for tweet in tweets:
        print(tweet.text)
        tw.append((liker_handles, tweet.text))
    return tw


def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words

def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words

def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

def remove_numbers(words):
    """Remove numbers from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r"([0-9])\w+", "", word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

def remove_newlines(words):
    new_words = []
    for word in words:
        if r'\n' in word:
            chars = word.split('')
            chars.remove(r'\n')
            new_words.append("".join(chars))
        else:
            new_words.append(word)
    return new_words


def remove_unistrings(words):
    """Remove loose strings"""
    new_words = []
    for word in words:
        if len(word) != 1:
            new_words.append(word)
    return new_words

def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    subset_words = [x for x in stopwords.words('spanish')]
    for word in words:
        if word not in subset_words:
            new_words.append(word)
    return new_words

def remove_hyperlinks(words):
    """Remove hyperlinks words from list of tokenized words"""
    new_words = []
    for word in words:
        if word.startswith('http'):
            continue
        else:
            new_words.append(word)
    return new_words

def remove_handles(words):
    """Remove twitter handles from list of tokenized words"""
    new_words = []
    for word in words:
        if word.startswith('@'):
            continue
        else:
            new_words.append(word)
    return new_words





def normalize(words):
    words = to_lowercase(words)
    words = remove_handles(words)
    words = remove_newlines(words)
    words = remove_hyperlinks(words)
    words = remove_non_ascii(words)
    words = remove_punctuation(words)
    words = remove_numbers(words)
    words = remove_unistrings(words)
    words = remove_stopwords(words)
    return words

def wc(data,title):
    plt.figure(figsize = (100,100))
    #mask = np.array(Image.open(pathtopic))
    wc = WordCloud(width=800, height=400, background_color = 'black', max_words = 1000,  max_font_size = 50)
    #image_colors = ImageColorGenerator(mask)
    wc.generate(' '.join(data))
    plt.imshow(wc) #.recolor(color_func = image_colors), interpolation = 'bilinear')
    plt.axis('off')
    plt.show()



def lootro(userhandle):
    username = 'TwisterData'
    password = 'bigdatainsta'
    scrolldowns = 4 # 0 Scrolldowns = 10 tweets, 212 likers.
                     # 10 Scrolldowns = 19 tweets.
                     # 100 Scrolldowns = 37 tweets.

    main_handle = userhandle




    options = Options()
    options.add_argument('--headless')
    print('Initializing ChromeDriver\n')
    browser = webdriver.Chrome(executable_path = "/Users/jeronimoluza/Desktop/scripts/chromedriver 4", options = options)
    print('Logging\n')
    Login(browser, username, password)
    print('Getting post links\n','Scrolls: ', scrolldowns, end = '\n')
    #img1 = 'https://twitter.com/' + main_handle +  '/photo'
    #browser.get(img1)
    #img2 = browser.find_element_by_xpath('//*[@id="react-root"]/div/div/div[1]/div/div/div/div/div[2]/div[2]/div[1]/div/div/div/div/div[2]/div/img')
    #img3 = img2.get_attribute('src')
    posts_links = Get_posts_links(browser,main_handle , scrolldowns)
    print('Number of tweets: ', len(posts_links), end ='\n')

    print('Getting likes \n')
    likes = Access_all_likes(posts_links)
    users = []
    try:
        #print('Browsing ',len(likes), 'likes lists for likers usernames', end = '\n')
        for x in likes:
            #print('Browsing ', x, 'for likers usernames', end = '\n')
            links = get_likers(browser, x)
            #print('Usernames', [x[1] for x in links], sep = ' -> ')
            users.append(links)
    except Exception as e:
        print(e)


    #browser.quit()

    likers = []
    for x in users:
        for y in x:
            if y[1] not in likers:
                likers.append(y[1])  

    print('Likers', likers, sep = ' -> ')

    tw = []

    import tweepy
    consumer_key='wz56XE96u7YLsWD9enoYXNJNV'
    consumer_secret='20Vn9OYD4ctrlyJBiAyNcv0kE4zgLbFzW8UqnhTzTCPNIBGaBc'
    access_token='1204395232755888128-JCZ0I7ysXSOhBB0qEWwL9USwgEaqTH'
    access_token_secret='ttBLaPewuiNUpj3oPjva1NYALUjCZoPuqkniyEJA78BAx'


    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)


    for tweet in tweepy.Cursor(api.user_timeline, id = main_handle).items(50):
        try:
            tweet.retweeted_status
        except:
            tw.append(tweet.text)





    browser.quit()

    vocab = []
    for x in tw:
        if type(x) == str:
            for word in normalize(x.split(' ')):
                vocab.append(word)


    wordcloud = wc(vocab,"Common Words")
    return wordcloud