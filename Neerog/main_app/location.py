import re
from geosky import geo_plug
replace_dictionary={"u00e9":"e","u00e1":"e","u0101":"a","u012b":"i","u016b":"u","u0100":"A","u016a":"u"}

#lis_of_countries = geo_plug.all_CountryNames() To get list of countries

def getCountries():
    return geo_plug.all_CountryNames()

def get_states(country):
    list1 = geo_plug.all_Country_StateNames()[1:].split("},")
    states = {}
    #country = request.GET.get("country")
    for i in list1:
        k = i.split(":")
        header = re.sub("{", "", re.sub("\"", "", k[0])).strip()
        trailing = re.sub("{", "", re.sub("\"", "", k[1])).strip()
        trailing = re.sub("\'", "", trailing)

        states[header] = trailing[1:len(trailing) - 1]
    for key, item in states.items():
        if (key == country):
            lis_of_states = item
    list_of_states=[]
    for i in lis_of_states.split(','):
        str1 = i.replace("\\", "")
        # print(str1)
        for key, value in replace_dictionary.items():
            if (str1.find(key) != -1):
                str1 = str1.replace(key, value)
        list_of_states.append(str1.strip())
    return list_of_states

def list_of_cities1(state):
    list_of_cities = []
    state = re.sub("\"", "", state).strip()
    city = geo_plug.all_State_CityNames(str(state))
    k = city.split(":")
    trailing = re.sub("\"", "", k[1])
    trailing = re.sub("}", "", re.sub("\]", "", re.sub("\[", "", trailing))).strip()
    lis_of_cities = trailing[0:len(trailing)].split(",")
    # lis_of_cities=list(re.sub("\]","",re.sub("\'","",re.sub("\[","",str(lis_of_cities)))))

    for i in lis_of_cities:
        str1 = i.replace("\\", "")
        # print(str1)
        for key, value in replace_dictionary.items():
            if (str1.find(key) != -1):
                str1 = str1.replace(key, value)
        list_of_cities.append(str1.strip())
    return list_of_cities
