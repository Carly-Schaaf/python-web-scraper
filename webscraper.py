from bs4 import BeautifulSoup 
import requests 
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgres+psycopg2://carly:Indy4running@localhost:5432/kites', echo=True)
Base = declarative_base()

class Kite(Base):
    __tablename__ = 'kites'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(Integer)
    link = Column(String)

def __repr__(self):
    return "<Kite(title='%s', price='%s', link='%s')>" % (
        self.title, self.price, self.link)

Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

kites = []

def return_next_page(page):
    url = f'http://www.windance.com/Used-Gear-Used-Kites/?page={page}'
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        return kites

    content = BeautifulSoup(response.content, "html.parser")
    kite_captions = content.select('.caption')

    for kite in kite_captions:
        title = kite.find_next('a').text[2:-2]
        price = float(kite.find_next('span').text[1:])
        link = kite.find_next('a')['href']
        id = link[-7:-1]

        formatted_kite = (id, title, price, link)
        kites.append(formatted_kite) 

    return return_next_page(page + 1)

all_kites = return_next_page(1)

for kite in all_kites:
    print(kite)
    kite = Kite(title=kite[0], price=kite[1], link=kite[2], id=kite[3])
    session.add(kite)

session.commit()

