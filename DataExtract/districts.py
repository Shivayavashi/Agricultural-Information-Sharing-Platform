from bs4 import BeautifulSoup
import requests
import urllib3
from pymongo import MongoClient

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

client = MongoClient("mongodb://localhost:27017/")
db = client["agritn"]
collection = db["districts"]
url = "https://www.tn.gov.in/district_view"
response = requests.get(url, verify=False)
req = response.content
soup = BeautifulSoup(req,"html.parser")
con = soup.find_all(class_ = "dir_listing")
districts = []
for i in con:
    details = {}
    details["name"] = i.find("a").text.strip()
    districts.append(details)

for district in districts:
    doc = {
        "districts" : district["name"]
    }

    existing_document = collection.find_one({"district name": district["name"]})

    if not existing_document:
        collection.insert_one(doc)
        print("Inserted")
    else:
        print("Skipped (Duplicate)")


 
