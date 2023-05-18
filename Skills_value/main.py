from selenium import webdriver
from bs4 import BeautifulSoup


parser = webdriver.Chrome()
url = 'https://hh.ru/search/vacancy?no_magic=true&L_save_area=true&text=&search_field=name&search_field=description&excluded_text=&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=100'
parser.get(url)
print(parser.page_source)

def next(parser):
    next_button = parser.find_element("class name", "bloko-button")
    next_button.click()