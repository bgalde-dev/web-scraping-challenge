# Import Dependencies

from webdriver_manager.chrome import ChromeDriverManager
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import config

# Defined function setting up Splinter

def init_browser():
    executable_path = {'executable_path' : ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)

# Utility function to parse the html made of a site and setting variables for the tag and class needed for each scrape
# find_all attribute is used to determine if between find_all() and find() is to be use.
def parse_page(browser, url, tag, class_name, find_all):
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    if find_all: 
        return soup.find_all(tag, {'class' : class_name})
    else: 
        return soup.find(tag, {'class' : class_name})

# Scrape function to scrape all needed features and create a dictionary from them.   
def scrape():
    browser = init_browser()
    mars_data = {}

    # News data
    latest_news = parse_page(browser, config.news_url, 'div', 'content_title', True)
    mars_data['news_title'] = latest_news[1].text

    latest_teaser = parse_page(browser, config.news_url, 'div', 'article_teaser_body', True)
    mars_data['news_p'] = latest_teaser[0].text

    # Image data
    image_soup = parse_page(browser, config.image_url, 'a', 'showimg', True)
    picture = image_soup[0]['href']
    mars_data['featured_image_url'] = config.image_url.replace('index.html', picture)

    # Hemisphere data
    hemi_soup = parse_page(browser, config.hemi_url, 'div', 'description', True)
    hemi_titles = []

    for item in hemi_soup:
        wrong_name = item.text.split('/')
        title = wrong_name[0].replace(' Enhancedimage', '')
        hemi_titles.append(title)

    hemi_images = []

    for url in config.hemi_url_list:
        hemi_soup = parse_page(browser, url, 'img', 'wide-image', False)
        hemi_images.append(config.hemi_base_url + hemi_soup['src'])

    hemisphere_image_urls = []

    for url in range(0, len(hemi_titles)):
        hemisphere_image_urls.append({'title':hemi_titles[url], 'img_url':hemi_images[url]})

    mars_data['hemisphere_image_urls'] = hemisphere_image_urls

    tables = pd.read_html(config.fact_url)
    fact_df = tables[0]

    # Only want the Mars header to show on the facts
    mars_fact_df = fact_df.rename(columns = {0 : ' ', 1 : 'Mars'})

    mars_table_str = mars_fact_df.to_html(index=False)
    mars_table_string = mars_table_str.replace('text-align: right;', 'text-align: left;')

    mars_data['mars_fact_table'] = mars_table_string

    #Close the browser
    browser.quit()
    return mars_data