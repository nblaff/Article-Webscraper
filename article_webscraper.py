# Importing relevant packages

import os
import smtplib
import imghdr
from email.message import EmailMessage
import requests, webbrowser, bs4, re
import pandas as pd
from bs4 import BeautifulSoup

# Random code stored in environment variable to help split the archived database later...

unique_code = os.environ.get('RANDOM_CODE_SEP')

EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

contacts = ['noahblaffpython@gmail.com', 'noah.blaff98@gmail.com']

email_contents = str()  
pg_current_articles = list() 
pg_new_articles = list() 

site = requests.get('http://www.paulgraham.com/articles.html', 'lxml') # Download website
soup = BeautifulSoup(site.content) # Turn into Beautiful Soup Object

my_table = soup.find_all('table')[2] # Find table with all main articles
children = my_table.findChildren('a') # Find all 'a' tags within table[2]

with open('articles_db.txt', 'r') as f: # TO DO --> Find a neater way to achieve the below
    pg_archived_articles = f.read()
    pg_archived_articles = pg_archived_articles.split(unique_code)

for child in children:
        pg_current_articles.append(child.get('href'))

for article in pg_current_articles:
    if article not in pg_archived_articles:
        pg_new_articles.append(article)
        
for article in pg_new_articles:
    with open('articles_db.txt', 'a') as file: 
        file.write(article + unique_code)

email_contents += 'New Paul Graham Essays:\n'

try: 
    for article in pg_new_articles:
        site = requests.get('http://paulgraham.com/' + article, 'lxml')
        soup = BeautifulSoup(site.content)
        images = soup.find('img', alt=True)
        title = images['alt']
        link = 'http://paulgraham.com/' + article
        contents = soup.find('font').text
        month = contents.split(' ')[0]
        for i in range(len(contents)):
            chunk = contents[i:i+4]
            if chunk.isdigit() is True:
                year = contents[i:i+4]
                break
        email_inp = '\nTitle: ' + title + '\n' + 'Link: ' + link + '\n' + 'Month: ' + month + '\n' + 'Year: ' + year + '\n'
        email_contents += email_inp
except:
    pass

lf_current_articles = list() 
lf_new_articles = list()

site = requests.get('https://longformarticles.net/', 'lxml') # Download website
soup = BeautifulSoup(site.content) # Turn into Beautiful Soup Object

my_table = soup.find_all('a', {"class": "page"}) # Find table with all main articles
num_pages = int(my_table[-1].text)
page_number = 1

email_contents += '\nNew Longform.net Essays:\n'

while page_number <= num_pages:
    site = requests.get('https://longformarticles.net/page/' + str(page_number), 'lxml') # Download website
    soup = BeautifulSoup(site.content) # Turn into Beautiful Soup Object
    articles = soup.find_all('article', 'post post--podcast js-post') # Find table with all main articles
    for i in range(len(articles)):
        title = articles[i].h2.text
        link = articles[i].a.get('href')
        date = articles[i].time.text
        lf_current_articles.append(link)
        email_inp = '\nTitle: ' + title + '\n' + 'Link: ' + link + '\n' + 'Date: ' + date + '\n'
        email_contents += email_inp
    page_number += 1

with open('articles_db.txt', 'r') as f:
    lf_archived_articles = f.read()
    lf_archived_articles = lf_archived_articles.split(unique_code)

for link in lf_current_articles:
    if link not in lf_archived_articles:
        lf_new_articles.append(link)
        with open('articles_db.txt', 'a') as f:
            f.write(link + unique_code)
    else: 
        continue
        
# print(email_contents)

msg = EmailMessage()
msg['Subject'] = 'New Articles/Reading Materials'
msg['From'] = EMAIL_ADDRESS
msg['To'] = ', '.join(contacts)

msg.set_content(email_contents)

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:    
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  
    smtp.send_message(msg)
