import http.client
import mimetypes
conn = http.client.HTTPSConnection("jobs.dou.ua")
payload = "csrfmiddlewaretoken=IzmzvW9SG13XkIOlJ7jkOUudWSu3eUSub7RXZ9bTRAODlSLeFpBuFNutJIcPhaNI&count=100"
headers = {
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Referer': 'https://jobs.dou.ua/vacancies/?category=QA',
  'Cookie': 'csrftoken=v3qAEgiQUzZ5DAsLMwiZ0JrHHB4fY7sRYBVY8tkR58KLEKpEIOA9RCrXurM11nn5; _ga=GA1.2.1422986327.1595190939; _gid=GA1.2.280644603.1595874143'
}
conn.request("POST", "/vacancies/xhr-load/?category=QA", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
