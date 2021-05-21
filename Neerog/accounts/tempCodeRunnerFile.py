phone=request.POST['phone']
    country=request.POST['country']
    state=request.POST['state']
    city=request.POST['city']
    area=request.POST['area']
    zip=int(request.POST['zip'])
    pic1=None
    specialization=request.POST.getlist('specialization')
    certificate=None

    if 'proof' in request.FILES:
        certificate = request.FILES['proof']
    else:
        messages.info(request,'Please Upload A Valid Licsense Or Certification Of Hospital.')
        return redirect("/accounts/signup/hospital")

    if 'pic1' in request.FILES:
        pic1 = request.FILES['pic1']

    speciality_pricing=dict()
    for sp in specialization:
        speciality_pricing[sp]=request.POST[sp]

    # Validation checks
    if(len(phone)==0):
        messages.info(request,"Invalid Phone Number! Phone Number can't be empty.")
    elif(len(phone)>10):
        messages.info(request,"Invalid Phone Number! Phone Number can't have more than 10 characters.")
    elif(authenticate.hasRegisteredPhone(phone, "Hospital")):
        messages.info(request,'This Phone is already registered!')
    else:
        phone=int(phone)
        if(request.user.is_authenticated):
            uid=request.user.id
            if(authenticate.registerHospital(uid, phone, country, state, city, zip, area, speciality_pricing, pic1, certificate)):
                messages.info(request,'Registeration Successful! Your account will be verified soon after review by our team.')
                return redirect("/")
            else:
                messages.info(request,"Registeration Failed!")
        else:
            messages.info(request,"Please Login Before Submitting Details!")
    return redirect("/accounts/signup/hospital")