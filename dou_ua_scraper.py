import json
import time
import traceback
import urllib
from time import sleep

import requests
from scrapy import Selector

from jobpost import jobpost

PROXIES_ENABLED = False

TELEGRAM_BOT_TOKEN = '1370354968:AAGKUbW7InioG3GYU4rubAM95TuMEz5GzyA'

ADMIN_ID = 461702056

PROXIES = {
    "http": "http://127.0.0.1:24000",
    "https": "http://127.0.0.1:24000",
}

POSTS_TO_SCRAPE_BY_ONE_REQUEST = 40
SECONDS_TO_SLEEP = 10
SECONDS_TO_SLEEP_BETWEEN_SCRAPING = 3

FILE_DATABASE = "jobs_database.txt"
JOB_POSTS_CATEGORY = 'qa'

PAYLOAD_URL = "https://jobs.dou.ua/vacancies/xhr-load/?category="
DOU_UA_JOB_POST_FEED_PAGE_URL = "https://jobs.dou.ua/vacancies/?category="

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
CSRF_TOKEN = 'LFWmSlQ94fiPmXZQ3Eomnusi9gnJTbRBR3JzKcyQjxVkJVYi1UC0pkAP3Yk1dvZw'
CSRF_MIDDLEWARE_TOKEN = "i1btRNuTX07X7qvAPKKtEKBVu4uXuSzOopYGJEcAciKsuou2N0Y7GAJsoMrfOcHJ"


def parse_job_post_from_response(response, counter):
    print(response)
    response_as_json = json.loads(response)
    response_html_from_json = response_as_json['html']
    elements = Selector(text=response_html_from_json).css('.l-vacancy .title a.vt')
    list_of_job_posts_for_page = []
    for element in elements:
        job_post = jobpost()
        counter[0] = counter[0] + 1
        job_link = element.attrib['href'].rsplit('/', 1)[0]
        job_title = element.xpath('text()').get()
        job_post.title = job_title
        job_post.url = job_link
        list_of_job_posts_for_page.append(job_post)

        print(counter)
        print(job_title)
        print(job_link)
        print()
    return list_of_job_posts_for_page


def fetch_job_posts_from_feed(offset):
    payload = "csrfmiddlewaretoken=" + CSRF_MIDDLEWARE_TOKEN + "&count=" + str(offset)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': USER_AGENT,
        'Referer': DOU_UA_JOB_POST_FEED_PAGE_URL + JOB_POSTS_CATEGORY,
        'Cookie': 'csrftoken=' + CSRF_TOKEN
    }
    if PROXIES_ENABLED:
        response = requests.request("POST", PAYLOAD_URL + JOB_POSTS_CATEGORY, headers=headers, data=payload,
                                    proxies=PROXIES)
    else:
        response = requests.request("POST", PAYLOAD_URL + JOB_POSTS_CATEGORY, headers=headers, data=payload)
    return response


def load_all_saved_job_post_urls():
    urls = []
    database_file_read = open(FILE_DATABASE, 'a+')
    database_file_read.seek(0)
    for line in database_file_read.readlines():
        urls.append(line.strip())
    database_file_read.close()
    return urls


def detect_new_job_posts(list_of_job_posts_scraped, list_of_job_posts_saved):
    list_of_new_job_posts = []
    for job_post in list_of_job_posts_scraped:
        if job_post.url not in list_of_job_posts_saved:
            list_of_new_job_posts.append(job_post)
    return list_of_new_job_posts


def save_new_job_posts(list_of_new_job_posts):
    database_file_write = open(FILE_DATABASE, 'a+')
    for job_post in list_of_new_job_posts:
        database_file_write.write(job_post.url + "\n")
    database_file_write.close()


def get_current_time():
    local_time = time.localtime()
    return time.strftime("%H:%M:%S %m.%m.%Y", local_time)


def send_to_telegram(list_of_new_job_posts):
    for new_job_post in list_of_new_job_posts:
        text = urllib.parse.quote(new_job_post.title +'\n\n' + new_job_post.url)
        url = 'https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN + '/sendMessage?chat_id=' + str(ADMIN_ID) + '&text=' + text
        requests.get(url)

if __name__ == '__main__':

    while True:
        try:
            offset = 0
            counter = [0]
            list_of_job_posts_scraped = []
            while True:
                response = fetch_job_posts_from_feed(offset)
                print(get_current_time() + ' | Sleeping for ' + str(
                    SECONDS_TO_SLEEP_BETWEEN_SCRAPING) + ' seconds and then scraping next page')
                sleep(SECONDS_TO_SLEEP_BETWEEN_SCRAPING)
                job_posts_from_response = parse_job_post_from_response(response.content, counter)
                for job_post in job_posts_from_response:
                    list_of_job_posts_scraped.append(job_post)
                offset = offset + POSTS_TO_SCRAPE_BY_ONE_REQUEST
                if len(job_posts_from_response) == 0:
                    break

            list_of_job_posts_saved = load_all_saved_job_post_urls()
            list_of_new_job_posts = detect_new_job_posts(list_of_job_posts_scraped, list_of_job_posts_saved)
            save_new_job_posts(list_of_new_job_posts)

            send_to_telegram(list_of_new_job_posts)

            print(get_current_time() + ' | Detected ' + str(len(list_of_job_posts_scraped)) + ' job posts')
            print(get_current_time() + ' | Found and saved ' + str(len(list_of_new_job_posts)) + ' new job posts')
            print(get_current_time() + ' | Sleeping for ' + str(SECONDS_TO_SLEEP) + ' seconds and then scraping new job posts')
            sleep(SECONDS_TO_SLEEP)
        except Exception as e:
            traceback.print_exc()
            print(get_current_time() + ' | Error happened:  ' + str(e))
            print(get_current_time() + ' | Sleeping for ' + str(
                SECONDS_TO_SLEEP) + ' seconds and then scraping new job posts')
            sleep(SECONDS_TO_SLEEP)
