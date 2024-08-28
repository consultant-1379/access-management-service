

#10 password to short
#11 password to long
#12 do not meet complexity
#20 missing CLI param
#22 Problem to create a session
#23 Password was not changed
#26 Issue with XML file
#27 Admin user and password not set for system
#28 Can't get SED from atvdit

from .models import ENMUserProfile, System
from externalfeeds import getters
from django.conf import settings
import sys, getopt, requests, json, time, os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import random
from datetime import datetime
from externalfeeds import encrypt_util
from requests.exceptions import RequestException
import logging

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger_object = logging.getLogger(__name__)
############################################################################################################
# Function validate provided password against constrains (password length, digits, lower and upper chars)  #
#----------------------------------------------------------------------------------------------------------#
# input:                                                                                                   #
#   password - provided in cli                                                                             #
# output:                                                                                                  #
#   return True if password is correct                                                                     #
#   sys.exit with code (10 password too short, 11 password too long and 12 if not meat rest of requirements#
############################################################################################################

def passwordValidation(password):
    minLength = 8
    maxLength = 32

    isLower = False
    isUpper = False
    isDigit = False
    isSpecial = False
    isUnwanted = False

    if len(password) < minLength:
        #print ("Password not long enaugh, password must be at least 8 characters")
        sys.exit(10)
    if len(password) > maxLength:
        #print ("Password too long, password must be not longer than 32 characters")
        sys.exit(11)
    for ch in password:
        if ch.isdigit():
            isDigit = True
        elif ch.islower():
            isLower = True
        elif ch.isupper():
            isUpper = True
        elif not ch.isalnum() and not ch.isspace():
            isSpecial = True
        else:
            isUnwanted = True

    if isDigit and isLower and isUpper and not isUnwanted:
        #print "Password has been validated"
        return True
    else:
        #print ("Password should have at last 1 uppercase letter, 1 lowercase letter, 1 special character, 1 digit.")
        sys.exit(12)

############################################################################################################
# ENM Login function                                                                                       #
#----------------------------------------------------------------------------------------------------------#
# input:                                                                                                   #
#   url -  url to ENM web interface                                                                        #
#   user - username who have Administrator priviliges                                                      #
#   password - password for provided user                                                                  #
# output:                                                                                                  #
#   s - user session                                                                                       #
#   sys.exit with code 22 on logon error                                                                   #
############################################################################################################

def login(url,user,password):
        #logger("INFO", "**Create session toward ENM**")
        s = requests.session()
        data = {"IDToken1": user, "IDToken2": password}
        resp = s.post(url+"login", data=data, verify=False, allow_redirects=False)
        if resp.status_code != 302:
                logger("ERROR", str(resp.status_code) +":"+ str(resp.content) + ".")
                return 22
                #sys.exit(22)
        #logger("INFO", "**Session created succesfully**")
        return s

def credential(enmname):
        
        Adminuser = False
        Adminpassword = False

        try:
            enm = System.objects.get(name=enmname)
        except System.DoesNotExist:
            enm = None
        
        if enm == None:
              logger("ERROR","Error. Can't get system from System.")
        else:
            if enm.admin == "":
                logger("ERROR","Admin user not set for system: "+ enmname)
            elif enm.password == "":
                logger("ERROR","Admin password not set for system:"+enmname)      
            else:
                Adminuser = enm.admin
                Adminpassword = encrypt_util.decrypt(enm.password)

        return Adminuser,Adminpassword

############################################################################################################
# ENM Logout function (terminate user session)                                                             #
#----------------------------------------------------------------------------------------------------------#
# input:                                                                                                   #
#   url -  url to ENM web interface                                                                        #
#   s - user session which will be terminated                                                              #
# output:                                                                                                  #
#   sys.exit with code 22 on logout error                                                                  #
############################################################################################################

def logout(url,s):
        #logger.info("INFO", "**End session toward ENM**")
        resp = s.get(url+"logout", verify=False, allow_redirects=False)
        if resp.status_code != 302:
              #print (resp.status_code)
              logger("ERROR", str(resp.status_code) +":"+ resp.content + ".")

              sys.exit(22)
              raise Exception ("ERROR"+str(resp.status_code) +":"+ resp.content + ".")
        s.close()
        #logger.info("INFO", "**Session terminated**")
        return

############################################################################################################
# User password reset                                                                                      #
#----------------------------------------------------------------------------------------------------------#
# input:                                                                                                   #
#   url -  url to ENM web interface                                                                        #
#   s - user session which will be terminated                                                              #
#   username - name of the user resetting the password                                                     #
#   userpassword - new password for the user                                                               #
############################################################################################################


def passwd(url,s,username,userpassword):
        logger("INFO", "**Reset user password for " + username + " on " + url + ".")
        data = {"username": username,"password": userpassword}
        headers = {"Content-Type": "application/json","Accept": "application/json"}
        resp = s.put(url+"oss/idm/usermanagement/changepassword", headers=headers, json=data, verify=False, allow_redirects=False)
        if resp.status_code != 204:
              #print ("You don't have account on " + url + ".   <br> ")
              logger("ERROR", str(resp.status_code) +":"+ str(resp.content) + ".")
              raise Exception ("ERROR"+ str(resp.status_code) +":"+ str(resp.content) + ".")
        else:
              logger("INFO", "Password hes been reset")
        return True

############################################################################################################
# User create function                                                                                     #
#----------------------------------------------------------------------------------------------------------#
# input:                                                                                                   #
#   url -  url to ENM web interface                                                                        #
#   s - object with user session                                                                           #
#   data - data prepared in dataPrepare for the user                                                       #
# output:                                                                                                  #
#   sys.exit with code 25 when user wont be created (only for single user creation                         #
############################################################################################################


def create(url,s,data):
        headers = {"Content-Type": "application/json","Accept": "application/json"}
        for u in data[:]:
                u = json.loads(u)
                logger("INFO", "**Creating user " + u["username"] + " on " + url + ".")
                resp = s.post(url+"oss/idm/usermanagement/users/", headers=headers, json=u, verify=False)
                if resp.status_code == 201:
                        logger("INFO", "User has been created.")
                        #print ("<p>User: " + u["username"] + " has been created " + url + "!</p>")
                else:
                        response = json.loads(resp.content)
                        logger("ERROR", str(resp.status_code) +":"+ response["userMessage"] + ".")
                        raise Exception ("ERROR" + str(resp.status_code) +":"+ response["userMessage"] + ".")
                        #print ("<p>User: " + u["username"] + " has not been created on " + url + "! " + response["userMessage"] + "</p>")
        return

############################################################################################################
# Preparing data string (dictianory) with user details                                                     #
#----------------------------------------------------------------------------------------------------------#
# input:                                                                                                   #
#   username -  username or list of usernames                                                              #
#   userpassword - password for new users (temp)                                                           #
#   privileges - list of privileges for created users                                                      #
# output:                                                                                                  #
#   data - generated data used by create function to add user to ENM system                                #
############################################################################################################


def dataPrepare(username,userpassword,privileges):
        status = "enabled"
        rolelist = "["
        for role in privileges[:]:
                rolelist = rolelist + '{"role": "' + role + '","targetGroup": "ALL"}'
                if len(privileges) > 1 and privileges.index(role) < len(privileges)-1:
                        rolelist = rolelist + ","
        rolelist = rolelist + "]"
        data = []
        for u in username[:]:
                tempData = '{"username":"' +  u + '","password":"' + userpassword + '","name":"' + u + '","surname":"' + u + '","status":"' + status + '", "passwordResetFlag": "true", "privileges":' + rolelist + '}'
                data.append(tempData)
                #logger("DEBUG", "**User Data**")
                #logger("DEBUG", "Username: "+u)
                #logger("DEBUG", "Status: "+status)
                #logger("DEBUG", "Priviliges: "+rolelist)
                #logger("DEBUG", "*************")
        return data

def batchadd(url,s,filename):
        delay = 0
        validator = 0

        while validator != 200:
                try:
                        f = {"usersFile": open('/home/eslakoz/ENM_test/'+filename, 'rb')}
                except IOError:
                        #print ("File does not exist!")
                        sys.exit(30)
                resp1 = s.post(url+"/oss/idm/usermanagement/importUsers?action=uploadFile", files=f, verify=False)
                if resp1.status_code == 422:
                        logout(url,s)
                        sys.exit(26)
                data = json.loads(resp1.text)
                time.sleep(delay)
                resp = s.post(url+"/oss/idm/usermanagement/importUsers?action=startAnalysis", json=data, verify=False, allow_redirects=False)
                validator = resp.status_code
                errortext = json.loads(resp.text)
                if resp.status_code == 422 and errortext["internalErrorCode"] == "UIDM-5-8-20":
                        delay = delay + 2
                elif resp.status_code != 200:
                        logout(url,s)
                        sys.exit(27)

        json_string = {"importId": data["importId"],"mode":"addNew"}
        resp = s.post(url+"/oss/idm/usermanagement/importUsers?action=startImport", json=json_string, verify=False, allow_redirects=False)
        if resp.status_code != 200:
                logout(url,s)
                sys.exit(28)
        time.sleep(2)
        resp = s.post(url+"/oss/idm/usermanagement/checkStatus", verify=False, allow_redirects=False)
        if resp.status_code != 200:
                logout(url,s)
                sys.exit(29)
        resp = s.post(url+"/oss/idm/usermanagement/importUsers?action=getReport", json=data, verify=False, allow_redirects=False)
        if resp.status_code != 200:
                logout(url,s)
                sys.exit(30)
        results = json.loads(resp.text)
        userresults =  results["userImportResult"]
        if results["importStatus"] == "SUCCESS" and userresults:
                for entry in userresults[:]:
                        print ("Username:" + entry["username"] + ", Status: " + entry["status"] + ", Error: " + entry["errorCode"])
        elif results["importStatus"] == "SUCCESS" and not userresults:
                print ("Users were updated")
        else:
                print ("Import failed!")
        return

############################################################################################################
# Check if user exist in ENM                                                                               #
#----------------------------------------------------------------------------------------------------------#
# input:                                                                                                   #
#   url -  url to ENM web interface                                                                        #
#   s - user session which will be terminated                                                              #
#   username - username of logged user (mainly Admin user in this case                                     #
# output:                                                                                                  #
#   0 - if logout will be successful                                                                       #
#   1 - in case of error                                                                                   #
############################################################################################################

def chkUserExist(url,s,username):
        resp = s.get(url+"/oss/idm/usermanagement/users/"+username, verify=False, allow_redirects=False)
        if resp.status_code != 200:
                return 1
        else:
                return 0

############################################################################################################
# Check if user exist in ENM                                                                               #
#----------------------------------------------------------------------------------------------------------#
# input:                                                                                                   #
#   url -  url to ENM web interface                                                                        #
#   s - user session which will be terminated                                                              #
#   username - username of logged user (mainly Admin user in this case                                     #
############################################################################################################


def userDel(url,s,username):
        userlist = username.split(",")
        for username in userlist[:]:
                logger("INFO", "**Delete user " + username + " form " + url + ".")
                if chkUserExist(url,s,username) == 0:
                        resp = s.delete(url+"/oss/idm/usermanagement/users/"+username)
                        if resp.status_code != 204:
                                #print ("User: " + username + " was not deleted " + url + " !<br>")
                                logger("ERROR", str(resp.status_code) +":"+ resp.content + ".")
                                raise Exception ("ERROR"+str(resp.status_code) +":"+ resp.content + ".")
                        else:
                                #print ("User: " + username + " has been deleted from " + url + " !<br>")
                                logger("INFO", "User  " + username + " has been deleted.")
                else:
                        #print ("User: " + username + " was not deleted! Account does not exist on " + url + " <br>")
                        logger("INFO", "User " + username + " does not exist on " + url + ".")
        return

def readRoles(usergroup):
        tempList = []
        usedGroups.append(usergroup)
        for x in uG[usergroup][:]:
                if x.isdigit():
                        tempList.append(x)
                elif x in uG and x != usergroup and x not in usedGroups:
                        readRoles(x)
        return tempList

def logger(type, message):
    if type == "INFO":
        logger_object.info(message)
    elif type == "ERROR":
        logger_object.error(message)
    elif type == "WARNING":
        logger_object.warning(message)
    elif type == "DEBUG":
        logger_object.debug(message)
    else:
        logger_object.info(message)

    return

def timestamp():
        return time.strftime("%x %X",time.gmtime())

def gen_password(system):

    if system == "ENM":
        head = "Enm"
        rand = str(random.randint(0,999))
        tail = "us"+str(random.randint(0,9))
        password = head+rand+tail
    else:
        password = "Ericssontemp1234"

    return password
    
       
def list_enm_users(system):
    
    dict = {}

    sed = getters.getSedFromDIT(str(system))['parameters']
    if sed == "none":
        raise Exception("DIT Error 28. Can't get SED for " + str(system))
    
    try:
        http_proxy = sed['httpd_fqdn']
    except: 
        raise Exception("No httpd_fqdn parameter forund in sed for: " + str(system) )


    base_url = "https://"+http_proxy+"/"
    check_url_connectivity(base_url)

    Adminuser,Adminpassword = credential(system)
    

    if Adminuser != False and Adminpassword != False:
    
        session = login(base_url,Adminuser,Adminpassword)
        if session == 22:
            raise Exception ("Error 22. Can't establish session towards ENM: " + str(system) + ". Wrong credentials")
        
        request = session.get(base_url+"/oss/idm/usermanagement/users/", verify=False, allow_redirects=False)
        logout(base_url,session)
        
        users = request.json()

        for i in range(0, len(users), 1):
                
                try:
                    dict[users[i]['username']] = datetime.strptime(users[i]['lastLogin'],'%Y%m%d%H%M%S%z') 
                except:
                    dict[users[i]['username']] = users[i]['lastLogin']
    else:
          raise Exception ("Error 27. Can't connect to ENM:" + str(system)+ "")
    
    return dict

def create_enm_account(account_name, system, account_profile):

    #print("Creating: ",account_name,"on:",system,"with Profile: ", account_profile)
    try:
        enmprofiles =  ENMUserProfile.objects.get(name = account_profile)
    except ENMUserProfile.DoesNotExist:
        enmprofiles = None

    #print("ENM Profile schema",enmprofiles.schema)

    tempList = []
    userpassword = gen_password("ENM")

    for schema in enmprofiles.schema.all():
        tempList.append(str(schema))
        #print(schema)    

    data =  dataPrepare(account_name.split(","),userpassword,tempList)
    #print("Account_name:",account_name)
    #print("Data:",data)

    sed = getters.getSedFromDIT(str(system))['parameters']
    
    if sed == "none":
          #print("Error 28. Can't get SED")
          return 28
    
    http_proxy = sed['httpd_fqdn']

    base_url = "https://"+http_proxy+"/"
    check_url_connectivity(base_url)
    
    Adminuser,Adminpassword = credential(system)

    if Adminuser != False and Adminpassword != False:
        session = login(base_url,Adminuser,Adminpassword)
        if session == 22:
            return 22
        
        create(base_url,session,data)
        logout(base_url,session)
    else:
        return 27

    return True

def reset_password_on_enm(account_name, system):
       
    userpassword = gen_password("ENM")
    
    sed = getters.getSedFromDIT(str(system))['parameters']
    if sed == "none":
          #print("Error 28. Can't get SED")
          return 28

    try:
        http_proxy = sed['httpd_fqdn']
    except:
        raise Exception("No httpd_fqdn parameter forund in sed for: " + str(system))

    base_url = "https://"+http_proxy+"/"
    check_url_connectivity(base_url)

    passwordValidation(userpassword)

    Adminuser,Adminpassword = credential(system)

    if Adminuser != False and Adminpassword != False:
        session = login(base_url,Adminuser,Adminpassword)
        if session == 22:
            return 22
        
        passwd(base_url,session,account_name,userpassword)
        logout(base_url,session)
        return userpassword
    else:
        return 27

def check_enmuser(account_name, system):

    sed = getters.getSedFromDIT(str(system.name))['parameters']
    if sed == "none":
          #print("Error 28. Can't get SED")
          return 28
    
    http_proxy = sed['httpd_fqdn']

    base_url = "https://"+http_proxy+"/"
    check_url_connectivity(base_url)

    Adminuser,Adminpassword = credential(system)

    if Adminuser != False and Adminpassword != False:
        session = login(base_url,Adminuser,Adminpassword)
        if session == 22:
            return 22
        
        userexist = chkUserExist(base_url, session, account_name)
        if userexist == 1:
           logger("INFO","User: " + account_name + " does not exist on " + system.name)
        else:
           logger("INFO","User: " + account_name + " exists on " + system.name)
        logout(base_url,session)
        #print (userexist)
        return userexist
    else:
        return 27

def remove_enm_account(account_name, system):
    
    sed = getters.getSedFromDIT(str(system))['parameters']
    http_proxy = sed['httpd_fqdn']
    try:
        http_proxy = sed['httpd_fqdn']
    except:
        raise Exception("No httpd_fqdn parameter forund in sed for: " + str(system))

    base_url = "https://"+http_proxy+"/"
    check_url_connectivity(base_url)

    Adminuser,Adminpassword = credential(system)

    if Adminuser != False and Adminpassword != False:
        session = login(base_url,Adminuser,Adminpassword)
        if session == 22:
            return 22
        
        userDel(base_url, session, account_name)
        userexist = chkUserExist(base_url, session, account_name)

        # if userexist == 1:
        #     print ("User: " + account_name + " does not exist on " + system + "!<br>")
        # else:
        #     print ("User: " + account_name + " exists on " + system + "!<br>")        
        logout(base_url,session)
        return userexist
    else:
        return 27

def check_url_connectivity(url, timeout=1, verify=False):
    try:
        response = requests.get(url, timeout=timeout,  verify=verify)
        if response.status_code == 200:
            return "URL: " +  url + " is reachable."
        else:
            return f"URL {url} returned a status code: {response.status_code}"
    except RequestException as e:

        raise RequestException(f"Error: {str(e)}")      