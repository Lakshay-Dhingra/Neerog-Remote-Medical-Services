from main_app.models import UserDetails, Doctor, Hospital, TestingLab, HospitalSpeciality
from main_app import user_data
import sys
# from django.db.models.functions import Lower
# from django.db.models import CharField

class SearchResult:
    # def __init__(self):
    #     self.name = "Pradeep Ahuja"
    #     self.phone = "8168832920"
    #     self.user_type = "Doctor"
    #     self.fee = "Rs. 200 Only."
    #     self.address = "Heart Care Clinic, Near XYZ School, Jhajjar Road, Rohtak, Haryana, India"
    #     self.uid = 5
    #     self.verified = "Yes"
    #     self.email = "lakshaydhingra32969@gmail.com"
    #     self.timings = "09:00 AM To 06:00 PM"
    def __init__(self):
        pass


def searchResults(searchtext):
    resultobjects = UserDetails.objects.exclude(user_type = "Patient").filter(name__icontains=searchtext)
    results = []
    for obj in resultobjects:
        if(user_data.isRegisteredUser(obj.userid+1)):
            sr = SearchResult()
            sr.name = obj.name
            sr.user_type = obj.user_type
            sr.email = obj.email
            sr.uid = obj.userid

            specificobj = None
            # try:
            if sr.user_type == "Doctor":
                specificobj = Doctor.objects.get(doctorid = sr.uid)
                if specificobj.is_independent:
                    sr.address = specificobj.clinic_name + ", " + specificobj.area + ", " + specificobj.city + ", " + specificobj.state + ", " + specificobj.country

                    sr.fee = specificobj.clinic_fee
                else:
                    hobj = specificobj.hospitalid
                    huserobj = hobj.hospitalid
                    hospitalid = huserobj.userid
                    sr.address = huserobj.name + ", " + hobj.area + ", " + hobj.city + ", " + hobj.state + ", " + hobj.country

                    hospitalspeciality=HospitalSpeciality.objects.get(hospitalid=hospitalid, speciality = specificobj.specialization)
                    sr.fee = hospitalspeciality.price
                sr.fee = "Rs. "+str(sr.fee)+" Only."

            elif sr.user_type == "Hospital":
                specificobj = Hospital.objects.get(hospitalid = sr.uid)
                sr.fee = "Depends On Specialization."
                sr.address = sr.name + ", " + specificobj.area + ", " + specificobj.city + ", " + specificobj.state + ", " + specificobj.country
            else:
                specificobj = TestingLab.objects.get(tlabid = sr.uid)
                sr.fee = "Depends On Medical Test."
                sr.address = sr.name + ", " + specificobj.area + ", " + specificobj.city + ", " + specificobj.state + ", " + specificobj.country
            # except:
            #     print(sys.exc_info())
            #     break

            sr.phone = specificobj.phone
            sr.verified = specificobj.verified
            if specificobj.start_time is None:
                sr.timings = "Not Specified"
            else:
                st = specificobj.start_time
                if st == "00:00":
                    st = "12:00 AM"
                elif st < "12:00":
                    st+= " AM"
                else:
                    hr=int(st[0:2])-12
                    if hr<10:
                        hr = "0"+str(hr)
                    else:
                        hr = str(hr)
                    st = str(hr) + st[2:]
                    st += " PM"
                
                et = specificobj.end_time
                if et == "00:00":
                    et = "12:00 AM"
                elif et < "12:00":
                    et+= " AM"
                else:
                    hr=int(et[0:2])-12
                    if hr<10:
                        hr = "0"+str(hr)
                    else:
                        hr = str(hr)
                    et = hr + et[2:]
                    et += " PM"

                sr.timings = st + " To " + et

            results.append(sr)
    return results