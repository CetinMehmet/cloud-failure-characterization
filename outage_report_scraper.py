import requests, os, simplejson
from datetime import timedelta, date

"""
    Using smart proxy manager from zyte.com
    API key: 70efafddbbad4fbb9a4bc9d87b404cfb
"""

URL_ID = {
    'aws': "T00%3A00%3A00-05%3A00;serviceId=57de1f2c1b43140e1b93b5aa",
    'azure': "T00%3A00%3A00-04%3A00;serviceId=59e1016bee5285254ea403a2"
}

START_DATE = date(2018, 1, 1)
END_DATE = date(2021, 1, 1)
META = "?returnMeta=true"


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def save_file(response_text, company, date):
    # Save the response
    PATH = os.getcwd() + "/" + company + "_reports/"
    FILE_NAME = PATH + date + '.json'

    # Write to file
    file = open(FILE_NAME, "w")
    if response_text != "":
        file.write(simplejson.dumps(simplejson.loads(response_text), indent=4))

    file.close()


def request_url(url):
    response = requests.get(
        url,
        # proxies={
        #     "http": "http://70efafddbbad4fbb9a4bc9d87b404cfb:@proxy.crawlera.com:8011/"
        # }
    )
    return response


def scrape(start_date, end_date):
    for key, value in URL_ID.items():
        company, url_id = key, value
        for single_date in daterange(start_date, end_date):
            date = single_date.strftime("%Y-%m-%d") # Convert date object to str
            url = "https://outage.report/api/chart;dateStr=" + date + url_id + META
            try:
                response = requests.get(
                    url,
                    proxies={
                        "http": "http://70efafddbbad4fbb9a4bc9d87b404cfb:@proxy.crawlera.com:8011/"
                    }
                )
                save_file(response.text, company, date)

                print("Successfully saved outage report from %s in %s" % (company, date))

            except (requests.exceptions.Timeout, requests.exceptions.HTTPError, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError):
                print(simplejson.dumps(dict(response.headers, indent=2)))
                continue
    


def main():
    scrape(START_DATE, END_DATE)

main()
