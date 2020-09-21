# Import Splinter, BeautifulSoup, Pandas, and Datetime
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=False)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere": hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

# Scrape Mars news
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Try/Except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None
    
    return news_title, news_p

# JPL Space Images Featured Image
def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Try/Except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

# Mars Facts
def mars_facts():
    # Try/Except for error handeling
    try:
        # Download tables as pandas df
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    # Assign columns and set index for dataframe
    df.columns=['description', 'Mars']
    df.set_index('description', inplace=True)

    # Covert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

# D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles
def hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    browser.is_element_present_by_css('div.class=item', wait_time=1)

    # Parse the data
    html = browser.html
    hemisphere_soup = soup(html, 'html.parser')

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    products = hemisphere_soup.find_all('div', class_='item')

    # Loop through products
    for product in products:
        hemispheres= {}
        title = product.find('h3').text
        page = product.find('a')['href']
        link = f'https://astrogeology.usgs.gov{page}'
        browser.visit(link)
        html = browser.html
        img_soup = soup(html, 'html.parser')
        img_link = img_soup.select_one('ul li a')['href']
        
        hemispheres = {'title':title,
                        'image':img_link}
        hemisphere_image_urls.append(hemispheres)

    return hemisphere_image_urls


if __name__ == "__main__":
    
    # If running as script, print scraped data
    print(scrape_all())