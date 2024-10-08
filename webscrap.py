from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import re

base_url = input("Enter the url: ")
linklist = []
linklist.append(base_url)
for url in linklist:
    response = requests.get(url, verify=False, timeout = 1000)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.findAll('a')
    try:
        data = soup.find('body').get_text()                                                                                                                                                                                                                                                                                                             
        print("title: ", soup.title.text)
        print("body: ", data)
        data=''.join(data.splitlines())
        url_without_punctuation = re.sub(r'[^\w\s]', '', base_url)
        file_name = "/llama2/localGPT_RAG/SOURCE_DOCUMENTS/"+url_without_punctuation + ".txt"
        if(soup.title.text == "404 Not Found"):
            continue
        # Open the file in write mode and save the scraped text to it
        else:
            with open(file_name, 'a+', encoding='utf-8') as file:
                file.write("\n\nTitle : " + soup.title.text)
                file.write("\n\nBody content : " + data)
                file.write("\n\n URL : "+url)
    except:
        continue
    
    if links:
        for link in links:
            href = link.get('href')  # Get the 'href' attribute of the anchor tag
            if href:
            # If the href is a full URL, append it directly, otherwise, join it with the base URL
                if href.startswith(base_url):
                    full_url = href
                else:
                    full_url = urljoin(base_url, href)
            if full_url.startswith(base_url) and full_url not in linklist:
              linklist.append(full_url)









