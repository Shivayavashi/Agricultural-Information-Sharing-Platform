from bs4 import BeautifulSoup
import requests
import urllib3
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["agritn"]
collection = db["uzhavarsandhai"]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
url = "https://www.agrimark.tn.gov.in/index.php/Infra/us_details"
response = requests.get(url)
req = response.content
soup = BeautifulSoup(req,"html.parser")
rows = soup.find('tbody').find_all('tr')
districtnames = []
uzhavarsandhai = []
open = []
close = []
for row in rows:
    columns = row.find_all('td')
    districtnames.append(columns[1].text.strip().lower())
    uzhavarsandhai.append(columns[2].text.strip().lower())
    open.append(columns[4].text.strip())
    close.append(columns[5].text.strip())

for i in range(len(districtnames)):
    doc = {
        "districts" : districtnames[i],
        "uzhavar sandhai" : uzhavarsandhai[i],
        "From" : open[i],
        "To" : close[i]
    }

    existing_document = collection.find_one({"uzhavar sandhai": uzhavarsandhai[i]})

    if not existing_document:
        collection.insert_one(doc)
        print("Inserted")
    else:
        print("Skipped (Duplicate)")




