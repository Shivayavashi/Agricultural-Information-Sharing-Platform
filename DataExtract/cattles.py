from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["agritn"]
collection = db["cattles"]

url = "https://agritech.tnau.ac.in/expert_system/cattlebuffalo/Breeds%20of%20cattle%20&%20baffalo.html"

response = requests.get(url)
req = response.content
soup = BeautifulSoup(req,"html.parser")
breed_name_elements = soup.find_all('b')

# Extract and print the cattle breed names
font_elements = soup.find_all('font', color="#ffff1f", size="+2")

# Extract and store the cattle breed names and descriptions
cattle_breeds_info = []

for font in font_elements:
    breed_name_element = font.find_next('b')
    if breed_name_element:
        breed_name = breed_name_element.get_text(strip=True)
        # Remove the serial number by splitting and taking the second part
        breed_name_parts = breed_name.split('. ')
        if len(breed_name_parts) > 1:
            breed_name_without_number = breed_name_parts[1]

            # Find the description for the current breed
            ul_element = breed_name_element.find_next('ul', class_='botanybullet')
            if ul_element:
                description_items = ul_element.find_all('li')
                description = [item.get_text(strip=True) for item in description_items]
                cattle_breeds_info.append({
                    'Name': breed_name_without_number,
                    'Description': description
                })

# Print the list of cattle breed names and descriptions
for info in cattle_breeds_info:
    print('Name:', info['Name'])
    print('Description:', info['Description'])
    print("-----------------------------------------------------------------------------------------------------------------------------")

for info in cattle_breeds_info:
    details = {
        "Name" : info['Name'],
        "Description" : info['Description']
    }

    existing_document = collection.find_one({"Name": info['Name']})
    
    if not existing_document:
        collection.insert_one(details)
        print("Inserted")
    else:
        print("Skipped (Duplicate)")
