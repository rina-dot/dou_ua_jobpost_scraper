import http.client
import json
from scrapy import Selector
from jobpost import Jobpost

DOU_UA_JOBPOST_FEED_PAGE_URL = "https://jobs.dou.ua/vacancies/?category=Qa"

def parse_jobpost_from_response(response, counter):
    response_as_json = json.loads(response)
    response_html_from_json = response_as_json['html']
    elements = Selector(text=response_html_from_json).css('.l-vacancy .title a.vt')
    list_of_job_posts_for_page = []
    for element in elements:
        jobpost = Jobpost()
        counter[0] = counter[0] + 1
        job_link = element.attrib['href']
        job_title = element.xpath('text()').get()
        jobpost.title = job_title
        jobpost.url = job_link
        list_of_job_posts_for_page.append(jobpost)

        print(counter)
        print(job_title)
        print(job_link)
        print()
    return list_of_job_posts_for_page


def fetch_jobposts_from_feed(offset):
    conn = http.client.HTTPSConnection("jobs.dou.ua")
    payload = "csrfmiddlewaretoken=IzmzvW9SG13XkIOlJ7jkOUudWSu3eUSub7RXZ9bTRAODlSLeFpBuFNutJIcPhaNI&count=" + str(
        offset)
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': 'https://jobs.dou.ua/vacancies/?category=QA',
        'Cookie': 'csrftoken=v3qAEgiQUzZ5DAsLMwiZ0JrHHB4fY7sRYBVY8tkR58KLEKpEIOA9RCrXurM11nn5; _ga=GA1.2.1422986327.1595190939; _gid=GA1.2.280644603.1595874143'
    }
    conn.request("POST", "/vacancies/xhr-load/?category=QA", payload, headers)
    res = conn.getresponse()
    data = res.read()
    response = data.decode("utf-8")
    return response


if __name__ == '__main__':
    print("start scraping")
    offset = 0
    step = 40
    counter = [0]
    list_of_job_posts = []
    while True:
        response = fetch_jobposts_from_feed(offset)
        jobposts_from_response = parse_jobpost_from_response(response, counter)
        list_of_job_posts.append(jobposts_from_response)
        offset = offset + step
        if len(jobposts_from_response) == 0:
            break
