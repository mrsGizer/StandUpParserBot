import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import requests
from bs4 import BeautifulSoup

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'event.db'))
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

class Events(Base):
        id = Column(Integer, primary_key=True)
        data_event = Column(DateTime, nullable=False)
        price_event = Column(String, nullable=True)
        availability = Column(String, nullable=True)
        url = Column(String, unique=True, nullable=False)

        def __init__(self, data_event, price_event, availability, url):
            self.data_event = data_event
            self.price_event = price_event
            self.availability = availability
            self.url = url

        def __repr__(self):
            return '<Events {} {} {}>'.format(self.data_event, self.price_event, self.url)

def get_html(url):
    try:
        result = requests.get(url)
        result.raise_for_status()
        return result.text
    except(requests.RequestExeption, ValueError):
        return False


def get_event(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_event = soup.findAll('div', class_="t778__wrapper no-underline")
    for event in all_event:
        data_event = event.find(
            'div',
            class_="t778__descr t-descr t-descr_xxs no-underline").text
        try:
            data_event = datetime.strptime(data_event, '%d %B, %H:%M')
        except(ValueError):
            data_event = datetime.now()
        price_event = event.find(
            'div',
            class_="t778__price t778__price-item t-name t-name_xs").text
        availability = event.find(
            'div',
            class_="t778__imgwrapper").text
        url = event.find(
            'div',
            class_="t778__bgimg t778__bgimg_first_hover t-bgimg js-product-img")['data-original']
        save_events(data_event, price_event, availability, url)


def pages(html):
    page = 1
    while page < 5:
        html = get_html('https://standupstore.ru/page/%s' % page)
        if html:
            get_event(html)
            with open('standup.html', 'w', encoding='utf8') as f:
                f.write(html)
        page += 1


def check_stand_up_site_page():
    html = get_html('https://standupstore.ru/')
    if html:
        pages(html)


def save_events(data_event, price_event, availability, url):
    new_event = Events(data_event=data_event, price_event=price_event, availability=availability, url=url)
    session.add(new_event)
    session.commit()


if __name__ == '__main__':
    check_stand_up_site_page()
   
