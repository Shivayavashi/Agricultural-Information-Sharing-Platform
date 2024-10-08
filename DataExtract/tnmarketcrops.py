from bs4 import BeautifulSoup
import requests
import urllib3
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["agritn"]
collection = db["districtcrops"]


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
url = "https://www.agrimark.tn.gov.in/index.php/Infra/comm_list"
response = requests.get(url)
req = response.content
soup = BeautifulSoup(req,"html.parser")
table = soup.find('table' ,class_ = 'table-bordered')
committee_names = []
crop_names = []
rows = table.find('tbody').find_all('tr')
for row in rows:
    columns = row.find_all('td')
    committee_names.append(columns[1].text.strip().lower())
    crop_names.append(columns[2].text.strip())

for i in range(len(committee_names)):
    details = {
        "districts" : committee_names[i],
        "crops" : crop_names[i] 
    }

    existing_document = collection.find_one({"committee_name": committee_names[i]})
    
    if not existing_document:
        collection.insert_one(details)
        print("Inserted")
    else:
        print("Skipped (Duplicate)")


    
