from bs4 import BeautifulSoup
import requests
from datetime import datetime
from models import PQDataModel

session_dict = dict()

def scrape_sessions():
    url = 'http://164.100.47.5/newsite/lob/lobarc.aspx'
    resp = requests.get(url, timeout=60)
    if resp.ok:
        soup = BeautifulSoup(resp.content, 'html.parser')
        table = soup.find(id="ctl00_ContentPlaceHolder1_GridView1")
        for tr in table.find_all('tr'):
            if tr.find('th'):
                continue
            session = tr.find('td').find('font').find('a').text
            from_date = tr.find_all('span')[0].text.strip()
            to_date = tr.find_all('span')[1].text.strip()
            fmt = "%d %b %Y"
            from_date = datetime.strptime(from_date, fmt).timestamp()
            to_date = datetime.strptime(to_date, fmt).timestamp()
            key = (from_date, to_date)
            session_dict[key] = session

def get_session(ip):
    for key in session_dict.keys():
        if key[0] <= ip <= key[1]:
            return session_dict[key]
    return '185'

def get_records():
    for q in PQDataModel.scan(PQDataModel.question_origin.startswith('rajyasabha')):
        from_date = q.question_date.timestamp()
        print(get_session(from_date))
        q.question_session = int(get_session(from_date))
        q.save()
        print(q.question_session)

if __name__ == '__main__':
    scrape_sessions()
    get_records()
