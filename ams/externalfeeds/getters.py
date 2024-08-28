import requests
from django.conf import settings
import logging
import json
from django.http import HttpResponse

logger = logging.getLogger(__name__)

def getENMURLFromFile(file_url, search_string):
    try:
        # Download the file
        response = requests.get(file_url,verify=False)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.RequestException as e:
        logger.debug(f'Error downloading file: {e}')
        return ""

    # Check if the response contains the expected content type
    content_type = response.headers.get('content-type', '')
    if 'text' not in content_type:
        logger.debug(f'Error: The content type is not text-based. Unable to search.')
        return ""

    # Get the content of the file
    file_content = response.text
    

    # Split the content into lines
    lines = file_content.splitlines()

    # Search for the string within each line
    for i, line in enumerate(lines, start=1):
         if search_string in line:
            logger.info(f'The search string "{search_string}" was found in line {i}: {line}')
            return line.split(',')[1].strip()

    # If the search string was not found in any line
    logger.debug(f'The search string "{search_string}" was not found in the file.')
    return ""

def response_check(response):

    if 200 <= response.status_code < 300:
        logger.info("Request to " + response.request.url +" successful")
    else:
        logger.warning("Request to"+ response.request.url + " failed with status code: " + str(response.status_code))


def getHydraToken(tokenPath):

    f = open(settings.BASE_DIR.__str__() + tokenPath, 'r') 
    if f.mode == 'r':
        token = f.read()
    f.close
    return token


def getInstanceFromHydra(instance):

    token = getHydraToken(tokenPath='/hydra_token')
    hydraUrl = "https://hydra.gic.ericsson.se/api/8.0/hql/instance"
    jsonString = {"query":"name='" + instance + "'"}

    headers = {'Content-Type': 'application/json', 'Authorization': token.strip()}
  
    request = requests.post(url=hydraUrl, headers=headers, verify=False, json=jsonString)
    response_check(request)


    return request.json()


def getCiFromHydra(ci):

    token = getHydraToken(tokenPath='/hydra_token')
    hydraUrl = "https://hydra.gic.ericsson.se/api/8.0/hql/ci"
    jsonString = {"query":"hostname='" + ci + "'"}
    headers = {'Content-Type': 'application/json', 'Authorization': token.strip()}
    request = requests.post(url=hydraUrl, headers=headers, verify=False, json=jsonString)
    response_check(request)
    return request.json()


def getCiId(ci):
    try:
        id=str(getCiFromHydra(ci)['result'][0]['id'])
    except:
        id=""
    return id



def getDeploymentFromDIT(deployment):
    
    dttUrl = "https://atvdit.athtem.eei.ericsson.se/api/deployments"
    query = "?q=name=" + deployment

    headers = {"Accept":"application/json"}
    
    request = requests.get(url=dttUrl+query, headers=headers, verify=False)
    response_check(request)
    return request.json()

def getSEDIdFromDIT(deployment_json):
    try:
        id=str(deployment_json[0]['enm']['sed_id'])
    except:
        id=""
    return id


def getDeploymentIdFromDIT(deployment_json):
    try:
        id=str(deployment_json[0]['_id'])
    except:
        id=""
    return id

def getDocContent(doc_json):
    try:
        content=doc_json[0]['content']
    except:
        content=""
    return content

def getVnflcmSedFromDIT(deployment):

    query = "?q=name=VNFLCM_" + deployment
    ditUrl = "https://atvdit.athtem.eei.ericsson.se/api/documents"

    headers = {"Accept":"application/json"}
    request = requests.get(url=ditUrl+query, headers=headers, verify=False)
    response_check(request)
    
    if request.json() == []:
        return json.loads('{"parameters":"none"}')
    else:
        return getDocContent(request.json())


def getCenmDeploymentValuesFromDIT(deployment):
    query = "?q=name=" + deployment + "_deployment_values"
    ditUrl = "https://atvdit.athtem.eei.ericsson.se/api/documents"

    headers = {"Accept":"application/json"}
    request = requests.get(url=ditUrl+query, headers=headers, verify=False)
    response_check(request)
    
    if request.json() == []:
        return json.loads('{"parameters":"none"}')
    else:
        return getDocContent(request.json())


def getSedFromDIT(deployment):
    deployment_json = getDeploymentFromDIT(deployment)
    response = []
    if deployment_json != []:
        query = "?q=_id=" + getSEDIdFromDIT(deployment_json)
        ditUrl = "https://atvdit.athtem.eei.ericsson.se/api/documents"

        headers = {"Accept":"application/json"}
    
        request = requests.get(url=ditUrl+query, headers=headers, verify=False)
    
        response_check(request)
        response= request.json()

    if response == []:
        httpd_fqdn = getENMURLFromFile(settings.ENM_NAMES_FILE, deployment)
        if httpd_fqdn :
            return json.loads('{"parameters":{"httpd_fqdn": "' + httpd_fqdn + '"}}')
        else:
            return json.loads('{"parameters":"none"}')
    else:
        return getDocContent(request.json())


def getDocumentFromDTT(deployment_id):
    query = "?q=deployment_id=" + deployment_id
    dttUrl = "https://atvdtt.athtem.eei.ericsson.se/api/documents"

    headers = {"Accept":"application/json"}
    request = requests.get(url=dttUrl+query, headers=headers, verify=False)
    response_check(request)

    return request.json()

def getDeploymentIdFromDTT(deployment_json):
    try:
        id=str(deployment_json[0]['_id'])
    except:
        id=""
    return id

def getDeploymentFromDTT(deployment):
    
    dttUrl = "https://atvdtt.athtem.eei.ericsson.se/api/deployments"
    query = "?q=name=" + deployment

    headers = {"Accept":"application/json"}
    request = requests.get(url=dttUrl+query, headers=headers, verify=False)
    response_check(request)

    return request.json()


def getBookingFromDTT(deployment_id):
    query = "?q=deployment_id=" + deployment_id
    dttUrl = "https://atvdtt.athtem.eei.ericsson.se/api/bookings"

    headers = {"Accept":"application/json"}
    request = requests.get(url=dttUrl+query, headers=headers, verify=False)
    response_check(request)

    return request.json()


def getRAMFromProm(instance, vpod, cluster):

    query = 'sum(kube_node_status_allocatable{vpod="' + vpod + '",dc="' + instance + '",program="DETS",resource="memory"})by('+ cluster +')-sum(kube_pod_container_resource_requests{vpod="'+ vpod +'",dc="' + instance + '",program="DETS",resource="memory"})by(' +  cluster + ')'
    promUrl = "http://http://10.117.246.164:9099/api/v1/query?query="
    logger.warning('log from MONITORING' + promUrl+ query)

    headers = {"Accept":"application/json", "Content-Type": "application/x-www-form-urlencoded"}
    request = requests.get(url=promUrl+query, headers=headers, verify=False)
    response_check(request)

    return request.json()

def getDDPLinkFromFile(file_url, search_string):
    try:
        # Download the file
        response = requests.get(file_url,verify=False)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.RequestException as e:
        logger.debug(f'Error downloading file: {e}')
        return ""

    # Check if the response contains the expected content type
    content_type = response.headers.get('content-type', '')
    if 'text' not in content_type:
        logger.debug(f'Error: The content type is not text-based. Unable to search.')
        return ""

    # Get the content of the file
    file_content = response.text

    # Split the content into lines
    lines = file_content.splitlines()

    # Search for the string within each line
    for i, line in enumerate(lines, start=1):
        if search_string in line:
            logger.debug(f'The search string "{search_string}" was found in line {i}: {line}')
            return line

    # If the search string was not found in any line
    logger.debug(f'The search string "{search_string}" was not found in the file.')
    return ""

def getVenmVersionFromFile(file_url, search_string):
    try:
        # Download the file
        response = requests.get(file_url,verify=False)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.RequestException as e:
        logger.debug(f'Error downloading file: {e}')
        return ""

    # Check if the response contains the expected content type
    content_type = response.headers.get('content-type', '')
    if 'text' not in content_type:
        logger.debug(f'Error: The content type is not text-based. Unable to search.')
        return ""

    # Get the content of the file
    file_content = response.text

    # Split the content into lines
    lines = file_content.splitlines()

    # Search for the string within each line
    for i, line in enumerate(lines, start=1):
         if search_string in line:
            logger.info(f'The search string "{search_string}" was found in line {i}: {line}')
            return line.split(',')[1].strip()

    # If the search string was not found in any line
    logger.debug(f'The search string "{search_string}" was not found in the file.')
    return ""


