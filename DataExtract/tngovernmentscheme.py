from bs4 import BeautifulSoup
import requests
import urllib3
import re
from pymongo import MongoClient
import spacy
from spacy.tokens import Doc, Span
client = MongoClient("mongodb://localhost:27017/")
db = client["agritn"]
collection = db["governmentschemes"]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

tamil_nadu_districts = [
    ("Chennai", ["Chennai", "Madras"]),
    ("Coimbatore", ["Coimbatore", "Kovai"]),
    ("Madurai", ["Madurai", "Madura"]),
    ("Tiruchirappalli", ["Tiruchirappalli", "Trichy"]),
    ("Tirunelveli", ["Tirunelveli", "Nellai"]),
    ("Salem", ["Salem", "Salem"]),
    ("Tiruppur", ["Tiruppur", "Tirupur"]),
    ("Erode", ["Erode", "Erode"]),
    ("Vellore", ["Vellore", "Vellore"]),
    ("Thoothukudi", ["Thoothukudi", "Tuticorin"]),
    ("Namakkal", ["Namakkal", "Namakkal"]),
    ("Thanjavur", ["Thanjavur", "Tanjore"]),
    ("Dindigul", ["Dindigul", "Dindigul"]),
    ("Ramanathapuram", ["Ramanathapuram", "Ramnad"]),
    ("Virudhunagar", ["Virudhunagar", "Virudhupatti"]),
    ("Nagapattinam", ["Nagapattinam", "Nagai"]),
    ("Krishnagiri", ["Krishnagiri", "Krishnagiri"]),
    ("Cuddalore", ["Cuddalore", "Cuddalore"]),
    ("Kanchipuram", ["Kanchipuram", "Kanchi"]),
    ("Thiruvallur", ["Tiruvallur", "Thiruvalur"]),
    ("Perambalur", ["Perambalur", "Perambalur"]),
    ("Ariyalur", ["Ariyalur", "Ariyalur"]),
    ("Tiruvannamalai", ["Tiruvannamalai", "Tiruvannamalai","Tirunvannamalai","Thirunvannamalai"]),
    ("Karur", ["Karur", "Karur"]),
    ("The Nilgiris", ["The Nilgiris", "Nilgiris"]),
]

# Function to extract district names from a sentence
def extract_districts(sentence):
    districts_found = []
    
    # Convert the sentence to lowercase for case-insensitive matching
    sentence = sentence.lower()
    
    # Iterate through each district and its alternate spellings
    for district, alternate_spellings in tamil_nadu_districts:
        for alternate_spelling in alternate_spellings:
            if alternate_spelling.lower() in sentence:
                districts_found.append(district.lower())
                break  # Break the inner loop if a match is found
    
    return districts_found

titles = []
funding_patterns = []
how_to_avail = []
descriptions = []
for i in range(3):
    url = "https://www.tn.gov.in/scheme/department_wise/2?page=" + str(i)
    print(url)
    response = requests.get(url, verify=False)
    req = response.content
    soup = BeautifulSoup(req,"html.parser")
    div_elements = soup.find_all('div', class_='scheme_lst')
    district_links = [divl.find('a')['href'] for divl in div_elements]
    for link in district_links:
        response = requests.get(link, verify=False)
        req = response.content
        soups = BeautifulSoup(req, 'html.parser')
        left_columns = soups.find_all("span", class_="left_column")

        # Loop through the left_column elements to find the target text
        for left_column in left_columns:    
            if "Title / Name" in left_column.get_text():
            # Extract the content from the corresponding right_column element
                title_content = left_column.find_next_sibling("span", class_="right_column").get_text(strip=True)
                titles.append(title_content)
            # Extract Title / Name
            if "Funding Pattern" in left_column.get_text():
                funding_content = left_column.find_next_sibling("span", class_ = "right_column").get_text(strip=True)
                funding_patterns.append(funding_content)
            if "How To Avail" in left_column.get_text():
                avail_content = left_column.find_next_sibling("span", class_ = "right_column").get_text(strip=True)
                how_to_avail.append(avail_content)
            if "Description" in left_column.get_text():
                desc_content = left_column.find_next_sibling("span", class_ = "right_column").get_text(strip=True)
                descriptions.append(desc_content)

districts = []
for d in descriptions:
    district = extract_districts(d)
    if district:
        districts.append(district)
    else:
        districts.append("all")


    
for existing_doc in collection.find():
    if existing_doc["Title"] not in titles:
        print("Removing:", existing_doc["Title"])
        collection.delete_one({"Title": existing_doc["Title"]})

for title, funding, avail, desc in zip(titles, funding_patterns, how_to_avail, districts):
    print("Title:", title)
    print("Funding Pattern:", funding)
    print("How To Avail:", avail)
    print("Description:", desc)
    print("-" * 40)

for title, funding, avail, disc in zip(titles, funding_patterns, how_to_avail, districts):
    scheme_data = {
        "Title": title,
        "Funding Pattern": funding,
        "How To Avail": avail,
        "Districts": disc
    }
    
    existing_document = collection.find_one({"Title": title})
    
    if not existing_document:
        collection.insert_one(scheme_data)
        print("Inserted:", title)
    else:
        print("Skipped (Duplicate):", title)


