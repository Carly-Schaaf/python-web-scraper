from bs4 import BeautifulSoup 
import requests 
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

while True:
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
            id = int(link[-6:-1])

            formatted_kite = (id, title, price, link)
            kites.append(formatted_kite) 

        return return_next_page(page + 1)

    all_kites = return_next_page(1)
    saved_kites = [kite.id for kite in session.query(Kite.id)]
    new_kites = []

    for kite in all_kites:
        kite = Kite(id=kite[0], title=kite[1], price=kite[2], link=kite[3])
        if kite.id not in saved_kites:
            session.add(kite)
            new_kites.append(kite)

    session.commit()

    def send_email(kites):
        port = 465
        password = open("password.txt").read()
        context = ssl.create_default_context()
        sender_email = "newkitealert@gmail.com"
        receiver_email = "carlyschaaf@berkeley.edu"

        message = MIMEMultipart("alternative")
        message["Subject"] = "New Kites"
        message["From"] = sender_email
        message["To"] = receiver_email

        # text = """\
        # New kites are in!

        # """
        kite_list_items = []

        for kite in new_kites:
            kite_list_items.append("""\
                    <li><a href={}>{}</a> - ${}</li>
            """.format(kite.link, kite.title, kite.price))

        html = """\
        <html>
        <body>
            <p>New kites are in!<br>
                {}
            </p>
        </body>
        </html>
        """.format("".join(kite_list_items))

        # part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # message.attach(part1)
        message.attach(part2)

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
    
    if new_kites:
        send_email(new_kites)
    
    time.sleep(86400)