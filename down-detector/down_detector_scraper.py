import requests, os, json, lxml.etree, re
from datetime import timedelta, date, datetime
import scrapy
from scrapy.selector import Selector
from bs4 import BeautifulSoup
import demjson, hjson
from dateutil.rrule import rrule, MONTHLY
import time



CLOUD_URL = {
    # "aws-amazon-web-services": "https://downdetector.com/status/aws-amazon-web-services/archive/",
    "windows-azure": "https://downdetector.com/status/windows-azure/archive/"
    # "google-cloud": "https://downdetector.com/status/google-cloud/archive/"
}

def request_url(url):
    response = requests.get(
        url,
        proxies={
            "https": "http://a29994b9b6ff4042b4770c7c6d781b19:@proxy.crawlera.com:8011/",
        },
        verify='/Users/mehmetberk.cetin/Desktop/zyte-proxy-ca.crt'
    )

    return response


def save_file(response_text, company, report_id):
    FILE_PATH = os.getcwd() + "/" + company + "/" + report_id + ".html"

    # Write to file
    file = open(FILE_PATH, "w")
    if response_text != "":
        file.write(response_text)

    file.close()

# TODO: Fix
def scrape_page(page):
    soup = BeautifulSoup(page, features='html.parser')
    div = soup.find(class_="justify-content-center")
    script = div.find('script')

    # file.write(data_json)
    jsonStr = str(script).strip()
    jsonStr = jsonStr.split('[')[1].strip()
    data = jsonStr.split(']')[0].strip()
    return [d.replace("\n", "").replace(" ", "").replace("'", '"') for d in [data]]


def months(start_month, start_year, end_month, end_year):
    start = datetime(start_year, start_month, 1)
    end = datetime(end_year, end_month, 1)
    return [(d.month, d.year) for d in rrule(MONTHLY, dtstart=start, until=end)]


def download_pages(outage_links, month, company):
    downdetector_url = "https://downdetector.com"
    if not outage_links:
        return print("No reports on month %s" % month)

    nr_reports = 0
    for link in outage_links:
        response = request_url(downdetector_url + link)
        report_id = link.split("/")[-2]

        save_file(response.text, company, report_id)
        nr_reports += 1

    return print("%s saved from month %s" % (nr_reports, month))


def scrape(dates):
    for key, value in CLOUD_URL.items():
        company, url_id = key, value

        for month_year in dates:
            date = str(month_year[1]) + "/" + str(month_year[0])
            print(company, date)
            url = url_id + date
            try:
                response = request_url(url)

                soup = BeautifulSoup(response.text, features='html.parser')
                href_links = soup.find_all('a')
                outage_links = [href.get('href') for href in href_links if str('/status/' + company + "/news/") in href.get('href')]

                download_pages(outage_links, date.split("/")[-1], company)

            except (requests.exceptions.Timeout, requests.exceptions.HTTPError, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError):
                print(simplejson.dumps(dict(response.headers, indent=2)))
                continue

            time.sleep(10)


        time.sleep(60)



def main():
    dates = months(start_month=1, start_year=2018, end_month=12, end_year=2020)
    scrape(dates)

main()
