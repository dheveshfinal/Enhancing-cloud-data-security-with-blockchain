from django.shortcuts import render,redirect
from .models import Encryptedmodel,Filerequestmodel
from django.contrib import messages
from .aes import encrypt, decrypt
from .ecc import *
import random
import base64
import json
from web3 import Web3
from django.conf import settings
from django.core.mail import send_mail


INDEXPAGE = "index.html"
loginpage = 'login.html'
regpage = 'reg.html'
viewowneracpt ='viewalluser.html'
cloudhomepage = 'cloudhome.html'
userhomepage = 'userhome.html'
ENCRYPTDATAPAGE = "encrypt.html"
VIEWFILESPAGE = "viewfiles.html"
FILEREQUESTPAGE = "filerequest.html"
SENDKEYPAGE = "sendkey.html"
DECRYPTPAGE = "decryptpage.html"
VIEWMYFILESPAGE = "viewmyfiles.html"
VIEWCLOUDFILESPAGE = "cloudfile.html"
VIEWFILESREQUESTPAGE = 'filerequestcloud.html'
# Create your views here.
one_account = "0x67c0dA8be0253598a3e5aCafF409D2D8Fa049B9F"
user_contract_address = "0x104fe79132165A7328efA26A219C6821A4E6FFcE"
web3=Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

with open("Blocks/build/contracts/UserContract.json") as abiFile:
    abidData = json.load(abiFile)
    abi = abidData["abi"]
    UserContract = web3.eth.contract(address=user_contract_address, abi=abi)


def index(req):
    return render(req,INDEXPAGE)

def login(request):
 if request.method == "POST":
        login_type = request.POST["login_type"]
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        if not login_type or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, loginpage)

        if login_type == "cloudserver":
            if email == "cloud@gmail.com" and password == "cloud":
                request.session["email"] = email
                request.session["name"] = "Cloud Server Admin"
                return render(request, cloudhomepage)
            else:
                messages.error(request, "Invalid cloud server credentials.")
                return render(request, loginpage)

        elif login_type == "user":
            try:
                id, name, email, contact, address, status = (
                    UserContract.functions.loginFunction(email, password).call(
                        {"from": one_account}
                    )
                )
                if status == "Deactivated":
                    messages.error(request, "User is not verified")
                elif "Invalid Users" != name:
                    request.session["email"] = email
                    request.session["name"] = name
                    request.session["useremail"] = email
                    return render(request, userhomepage, {"user": user})
                else:
                    messages.error(request, "Invalid user credentials ")

                return render(request, loginpage)

            except:
                messages.error(
                    request, "Invalid user credentials or account not activated."
                )
                return render(request, loginpage)
        else:
            messages.error(request, "Invalid login type selected.")
        return render(request, loginpage)
 return render(request, loginpage)
        
                
def user(request):
    if request.method == "POST":
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        conpasword = request.POST.get("password2", "")
        contact = request.POST.get("contact", "")
        address = request.POST.get("address", "")
        if password == conpasword:

            data = UserContract.functions.checkEmail(email).call({"from": one_account})
            print(data)
            if data == "Success":
                UserContract.functions.AddUsers(
                    name, email, password, contact, address, "Deactivated"
                ).transact({"from": one_account, "gas": "600000"})
                return render(request, loginpage)
            else:
                messages.warning(request, "Email already exists.")
                return redirect("user")
        else:
            return render(request, regpage)
    return render(request, regpage)



def cloudhome(req):
    return render(req, cloudhomepage)

def viewusers(request):
    id, name, email, contact, address, status = (
        UserContract.functions.getUsersActivated("Deactivated").call(
            {"from": one_account}
        )
    )
    nothing = UserContract.functions.getUsersActivated("Deactivated").call(
        {"from": one_account}
    )
    usersdata = []
    print(nothing)
    for i in range(len(id)):
        if id[i] != 0:
            usersdata.append(
                {
                    "id": id[i],
                    "name": name[i],
                    "email": email[i],
                    "contact": contact[i],
                    "address": address[i],
                    "status": status[i],
                }
            )

    return render(request, viewowneracpt, {"usersdata": usersdata})

# cloud server accept the user request
def acceptuser(request, id):

    UserContract.functions.upldateState(int(id), "Activate").transact(
        {"from": one_account}
    )
    messages.success(request, f"The User  has been successfully activated.")
    return redirect("viewusers")

def encryptdata(req):
    if req.method=="POST":
        data = req.POST['message']
        if req.POST['algorithm'] =="aes":
            randomkey = str(random.randint(000000,999999))
            secret_key =randomkey.encode()
            # Original data
            data = data.encode()
            # Encrypt data
            aesencrypted_data = encrypt(data, secret_key)
            path = os.path.join("static/AES/encryptedfiles/example.txt")
            with open(path, 'w') as file:
                # Write data to the file
                file.write(f"{aesencrypted_data}")
            # Decrypt the message using the Fernet cipher
            aesdecrypted_data = decrypt(aesencrypted_data, secret_key)
            aesdecrypted_data = aesdecrypted_data.decode('utf-8')
            print(f"Decrypted Data: {aesdecrypted_data}")
            path = os.path.join("static/AES/files/example.txt")
            with open(path, 'w') as file:
                # Write data to the file
                file.write(f"{aesdecrypted_data}")
            encrypt_text = Encryptedmodel(
                useremail = req.session['useremail'],
                textcontent = aesencrypted_data,
                filekey = secret_key,
                encfilepath="static/AES/encryptedfiles/example.txt",
                decfilepath="static/AES/files/example.txt"
            )
            encrypt_text.save()
        elif req.POST['algorithm'] == "ecc" :
            # Encrypt a message using the Fernet cipher
            randomkey = str(random.randint(000000,999999))
            secret_key =randomkey.encode()
            message = data.encode('utf-8')
            encrypted_message = fernet_key.encrypt(message)
            decrypted_message = fernet_key.decrypt(encrypted_message)
            path = os.path.join("static/ECC/encryptedfiles/example.txt")
            with open(path, 'w') as file:
                # Write data to the file
                file.write(f"{encrypted_message}")
            
            

            decrypted_message = decrypted_message.decode('utf-8')
            path = os.path.join("static/ECC/files/example.txt")
            with open(path, 'w') as file:
                # Write data to the file
                file.write(f"{decrypted_message}")
            encrypt_text = Encryptedmodel(
                useremail = req.session['useremail'],
                textcontent = encrypted_message,
                filekey = secret_key,
                encfilepath="static/ECC/encryptedfiles/example.txt",
                decfilepath="static/ECC/files/example.txt"
            )
            encrypt_text.save()

            
        messages.success(req,"File Created Successfully")
        return render(req,ENCRYPTDATAPAGE)
    return render(req,ENCRYPTDATAPAGE)

def viewfiles(req):    
    # encrypted_data = Encryptedmodel.objects.filter(useremail=req.session['useremail'])
    # if encrypted_data:
    #     return render(req,VIEWFILESPAGE,{'encrypted_data':encrypted_data,'file':'yesfile'})
    # else:
    encrypted_data = Encryptedmodel.objects.exclude(useremail =req.session['useremail'])
    return render(req,VIEWFILESPAGE,{'encrypted_data':encrypted_data,'file':'nofile'})


def viewcloudfiles(req):    
    # encrypted_data = Encryptedmodel.objects.filter(useremail=req.session['useremail'])
    # if encrypted_data:
    #     return render(req,VIEWFILESPAGE,{'encrypted_data':encrypted_data,'file':'yesfile'})
    # else:
    encrypted_data = Encryptedmodel.objects.all()
    return render(req,VIEWCLOUDFILESPAGE,{'encrypted_data':encrypted_data,'file':'nofile'})


def viewfilesrequest(req):    
    data = Filerequestmodel.objects.all()
    return render(req,VIEWFILESREQUESTPAGE,{'filedata':data})
    # return render(req,VIEWFILESREQUESTPAGE,{'encrypted_data':encrypted_data,'file':'nofile'})

def sendrequest(req,id):
    print(id)
    data =[(j.id,j.useremail,j.textcontent,j.filekey) for j in Encryptedmodel.objects.filter(id=id)]
    print("=========")
    print(data)
    filerequest = Filerequestmodel(
        fileid=data[0][0],
        useremail = data[0][1],
        textcontent = data[0][2],
        filekey = data[0][3],
        receiveremail=req.session['useremail'])
    filerequest.save()
    return redirect("viewfiles")


def filerequest(req):
    data = Filerequestmodel.objects.filter(useremail=req.session['useremail'],status='pending')
    return render(req,FILEREQUESTPAGE,{'filedata':data})


def sendkey(req,fileid):
    print(fileid)
    dc = [(i.filekey,i.receiveremail) for i in Filerequestmodel.objects.filter(fileid=fileid,useremail=req.session['useremail'],status='pending')]
    print(dc)
    
    subject = "No reply"
    cont = 'The private key to decrypt file.'
    key = dc[0][0]
    m1 = "This message is automatic generated so dont reply to this Mail"
    m2 = "Thanking you"
    m3 = "Regards"
    m4 = "Cloud Service Provider."
    Email = dc[0][1]
    print(key)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [Email]
    text = cont + '\n' + key + '\n' + m1 + '\n' + m2 + '\n' + m3 + '\n' + m4
    send_mail(subject, text, email_from, recipient_list,fail_silently=False,)
    dc = Filerequestmodel.objects.filter(fileid=fileid,useremail=req.session['useremail'],status='pending').last()
    dc.status = 'approved'
    dc.save()
    return redirect("filerequest")


def decryptdata(req):
    data = Filerequestmodel.objects.filter(status='approved',receiveremail=req.session['useremail'])
    return render(req,DECRYPTPAGE,{"filedata":data})


def viewmyfiles(req,id):
    if req.method=="POST":
        print("----------------")
        filekey = req.POST['filekey']
        secret_key =filekey.encode('utf-8')
        print(filekey)

        try:
            aesencrypted_data = [(i.decfilepath) for i in Encryptedmodel.objects.filter(filekey=secret_key)][0]
            print(aesencrypted_data)
            with open(aesencrypted_data,"r") as f:
                content = f.read()
            print(content)
            return render(req,VIEWMYFILESPAGE,{'id':id,'files':'False','content':content})
        except:
            messages.warning(req,"Key is not valid...!")
            return render(req,VIEWMYFILESPAGE,{'id':id,'files':'True'})
            
    return render(req,VIEWMYFILESPAGE,{'id':id,'files':'True'})

        