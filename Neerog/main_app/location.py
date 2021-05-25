import re
from geosky import geo_plug
replace_dictionary={"u00e9":"e","u00e1":"e","u0101":"a","u012b":"i","u016b":"u","u0100":"A","u016a":"u"}

#lis_of_countries = geo_plug.all_CountryNames() To get list of countries

def getCountries():
    return geo_plug.all_CountryNames()

def get_states(country):
    list1 = geo_plug.all_Country_StateNames()[1:].split("},")
    states = {}
    print(type(list1))
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
    lis_of_states=lis_of_states.strip()
    l=lis_of_states.encode('utf-8-sig',"replace").decode("unicode-escape")
    k12=0;
    for i in l.split(','):
        #str=i
        #str.encode(encoding="utf-8")
        #print(str)
        #str1 = i.replace("\\", "")
        # print(str1)
        """for key, value in replace_dictionary.items():
            if (str1.find(key) != -1):
                str1 = str1.replace(key, value)"""
        if(k12==0):
            str2=i.strip()[3:]
            list_of_states.append(str2)
        else:
            list_of_states.append(i.strip())
        #print(list_of_states,lis)
        k12+=1;
    return list_of_states

def list_of_cities1(state):
    list_of_cities = []
    state = re.sub("\"", "", state).strip()
    city = geo_plug.all_State_CityNames(str(state))
    k = city.split(":")
    trailing = re.sub("\"", "", k[1])
    trailing = re.sub("}", "", re.sub("\]", "", re.sub("\[", "", trailing))).strip()
    l = trailing[0:len(trailing)].encode('utf-8-sig',"replace").decode("unicode-escape")
    lis_of_cities=l.split(",")
    for i in range(0,len(lis_of_cities)):
        #str1 = i.replace("\\", "")
        # print(str1)
        """for key, value in replace_dictionary.items():
            if (str1.find(key) != -1):
                str1 = str1.replace(key, value)"""
        if(i==0):
            p=lis_of_cities[i][3:]
            list_of_cities.append(p.strip())
        else:
            list_of_cities.append(lis_of_cities[i].strip())

    return list_of_cities
