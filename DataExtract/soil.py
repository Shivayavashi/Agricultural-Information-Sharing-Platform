from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["agritn"]
collection = db["soil"]

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


url = "https://agritech.tnau.ac.in/agriculture/agri_soilresource_agroclimate.html"
response = requests.get(url)
req = response.content
soup = BeautifulSoup(req, "html.parser")
table = soup.find('table')
rows = table.find_all('tr')

# Initialize lists to store extracted data
zone_data = []
district_data = []
soil_type = []
# Iterate through the rows and extract data
for row in rows[1:]:
    columns = row.find_all('td')
    if len(columns) == 3:  # Ensure that the row has three columns
        zone_data.append(columns[0].get_text().strip())
        district_data.append(columns[1].get_text().strip().lower())
        soil_type.append(columns[2].get_text().strip())

districts = []
for d in district_data:
    district = extract_districts(d)
    if district:
        districts.append(district)
    else:
        districts.append("all")

for i in range(len(zone_data)):
    details = {
        "zone" : zone_data[i],
        "districts" : districts[i],
        "soil type" : soil_type[i] 
    }

    existing_document = collection.find_one({"zone": zone_data[i]})
    
    if not existing_document:
        collection.insert_one(details)
        print("Inserted")
    else:
        print("Skipped (Duplicate)")
