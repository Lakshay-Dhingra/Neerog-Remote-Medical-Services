import sys
 
def scrape_specialities():    
    #This code scraps from wikipedia article "https://en.wikipedia.org/wiki/Medical_specialty", the list of medical specialities.
    #This code doesn't fetches data at runtime (It'll make website slow and can break the system on change in original website...), it's just for reference...
    import requests
    from bs4 import BeautifulSoup
    url="https://en.wikipedia.org/wiki/Medical_specialty"
    htmlContent = requests.get(url).content
    soup = BeautifulSoup(htmlContent, 'html.parser')
    table = soup.find_all("table",class_="wikitable")[2]
    table_rows = table.find_all("tr")
    print("(",end="")
    for row in table_rows:
        column = row.find("td")
        if(column != None):
            print("'"+str(column.find("a").get('title'))+"'", end=", ")
    print(")")

def get_specialities():
    #List of medical specialities
    return ('Anaesthesia', 'Dermatology', 'Emergency medicine', 'Cardiac Surgery', 'Family medicine', 'Internal medicine', 'Neurology', 'Obstetrics and Gynecology', 'Ophthalmology', 'Orthopedic surgery', 'Otolaryngology', 'Oral and Maxillofacial Surgery', 'Pediatrics', 'Podiatry', 'Psychiatry', 'Radiology', 'Surgery', 'Urology', 'Neurosurgery', 'Plastic surgery', 'Gastroenterology', 'Pulmonology')

if __name__ == '__main__':
    globals()[sys.argv[1]]()