from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import urllib.request


class CraiglistScraper(object):
    def __init__(self, location, postal, max_price, radius, car_name):
        self.location = location
        self.postal = postal
        self.max_price = max_price
        self.radius = radius
        self.car_name = car_name
        
        self.url = f"https://{location}.craigslist.org/search/cta?query={car_name}&srchType=T&hasPic=1&postedToday=1&search_distance={radius}&postal={postal}&max_price={max_price}"
    
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.delay = 3

    def load_craigslist_url(self):
        self.driver.get(self.url)
        try:
            wait = WebDriverWait(self.driver, self.delay)
            wait.until(EC.presence_of_element_located((By.ID, "searchform")))
            #print("Page is ready")
        except TimeoutException:
            print("Loading took too much time")

    def extract_post_information(self):
        all_posts = self.driver.find_elements_by_class_name("result-row")

        dates = []
        titles = []
        prices = []

        for post in all_posts:
            title = post.text.split("$")

            if title[0] == '':
                title = title[1]
            else:
                title = title[0]

            title = title.split("\n")
            price = title[0]
            title = title[-1]

            title = title.split(" ")

            month = title[0]
            day = title[1]
            title = ' '.join(title[2:])
            date = month + " " + day

            #print("PRICE: " + price)
            #print("TITLE: " + title)
            #print("DATE: " + date)

            titles.append(title)
            prices.append(price)
            dates.append(date)

        return titles, prices, dates

    def extract_post_urls(self):
        url_list = []
        html_page = urllib.request.urlopen(self.url)
        soup = BeautifulSoup(html_page, "lxml")
        for link in soup.findAll("a", {"class": "result-title hdrlnk"}):
            print(link["href"])
            url_list.append(link["href"])
        return url_list

    def quit(self):
        self.driver.close()


location = "vancouver"
postal = "V3R 7Z9"
max_price = "10000"
radius = "500"
car_list = ["rx7", "mr2", "toyota"]
for i in range(len(car_list)):
    scraper = CraiglistScraper(location, postal, max_price, radius, car_list[i])
    scraper.load_craigslist_url()
    titles, prices, dates = scraper.extract_post_information()
    if len(titles) != 0:
        print(car_list[i] + " has new listing today!!!")
    else:
        print("no new listing of " + car_list[i] + " today")
    print("------------------------------------------")