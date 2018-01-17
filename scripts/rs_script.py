import mechanicalsoup
import bs4


def main():
    # Connect to duckduckgo
    browser = mechanicalsoup.StatefulBrowser()
    browser.open("http://164.100.47.5/qsearch/qsearch.aspx")

    # Fill-in the search form
    browser.select_form('#aspnetForm')

    browser["ctl00$ContentPlaceHolder1$ddlqtype"] = "ANYTYPE"
    browser["ctl00$ContentPlaceHolder1$ddlsesfrom"] = "244"
    browser["ctl00$ContentPlaceHolder1$ddlsesto"] = "244"
    browser["ctl00$ContentPlaceHolder1$btnALL"] = "AllRec."
    browser.submit_selected(btnName="ctl00$ContentPlaceHolder1$btnALL")

    print(browser.list_links())

    # Display the results
    # for link in browser.get_current_page().select('tr.td'):
    #     print(link)
    #     print(link.text, '->', link.attrs['href'])


if __name__ == '__main__':
    main()