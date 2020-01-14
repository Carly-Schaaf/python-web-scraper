from bs4 import BeautifulSoup 
import requests 

url = 'http://www.windance.com/Used-Gear-Used-Kites/'
response = requests.get(url, timeout=5)
content = BeautifulSoup(response.content, "html.parser")
kites = [kite.text[2:-2] for kite in content.findAll('a', attrs={'class': 'productnameTitle'})]

print(kites)


def return_next_page(soup):
    """
    return next_url if pagination continues else return None

    Parameters
    -------
    soup - BeautifulSoup object - required

    Return 
    -------
    next_url - str or None if no next page
    """
    next_url = soup.find('a', {'class': 'next'}) or None
    
    print(next_url)

return_next_page(content)