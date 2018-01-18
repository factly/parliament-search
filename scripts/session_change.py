from bs4 import BeautifulSoup
import requests


def main():
    url = 'http://164.100.47.5/newsite/lob/lobarc.aspx'
    resp = requests.get(url, timeout=60)
    if resp.ok:
        soup = BeautifulSoup(resp.content, 'html.parser')
        table = soup.find(id="ctl00_ContentPlaceHolder1_GridView1")
        for tr in table.find_all('tr'):
            if tr.find('th'):
                continue
            session = tr.find('td').find('font').find('a').text
            print(session)
            for ts in tr.find_all('span'):
                print(ts.text.strip())


if __name__ == '__main__':
    main()
