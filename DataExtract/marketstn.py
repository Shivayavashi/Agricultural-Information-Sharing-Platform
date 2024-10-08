from bs4 import BeautifulSoup
import requests
import urllib3
from pymongo import MongoClient
#table table-bordered table-striped example dataTable no-footer
client = MongoClient("mongodb://localhost:27017/")
db = client["agritn"]
collection = db["regulatedmarket"]

url = "https://www.agrimark.tn.gov.in/index.php/Infra"
response = requests.get(url)
req = response.content
soup = BeautifulSoup(req,'html.parser')
text = soup.find('table', class_ = "table table-bordered table-striped example dataTable no-footer")
committee_names = []
regulated_markets = []
no_of_godowns = []
capacity_of_godowns = []
rows = soup.find('tbody').find_all('tr')
for row in rows:
    columns = row.find_all('td')
    committee_names.append(columns[1].text.strip().lower())
    regulated_markets.append(columns[2].text.strip().lower())
    no_of_godowns.append(columns[3].text.strip())
    capacity_of_godowns.append(columns[4].text.strip())

for i in range (len(committee_names)):
    doc = {
        "districts" : committee_names[i],
        "regulated market" : regulated_markets[i],
        "no. of godowns" : no_of_godowns[i],
        "capacity of godowns" : capacity_of_godowns[i]
    }

    existing_document = collection.find_one({"regulated market": regulated_markets[i]})

    if not existing_document:
        collection.insert_one(doc)
        print("Inserted")
    else:
        print("Skipped (Duplicate)")



