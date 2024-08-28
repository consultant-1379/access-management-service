import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)



class JiraService:
    def __init__(self):
        self.base_url = settings.JIRA_API_URL
        self.auth  = HTTPBasicAuth(settings.JIRA_USERNAME, settings.JIRA_API_TOKEN)

    def create_issue(self, issue_data):
        endpoint = f"{self.base_url}/issue"
        headers = {"Content-Type": "application/json"}
        response = requests.post(endpoint, json=issue_data, headers=headers, auth=self.auth)
        if response.status_code == 201:
            logger.info("Created ticket: " + response.json().get("key"))
            return response.json()
        else:
            logger.error(f"JIRA Failed to create issue: {response.status_code} - {response.text}")
            raise Exception(f"JIRA Failed to create issue: {response.status_code} - {response.text}")
            
    
    def add_comment(self, issue_key, comment_body):
        endpoint = f"{self.base_url}/issue/{issue_key}/comment"
        headers = {"Content-Type": "application/json"}
        data = {"body": comment_body}

        try:
            response = requests.post(endpoint, json=data, headers=headers, auth=self.auth)

            if response.status_code == 201:
                logger.info("JIRA Added comment to  ticket: " + issue_key)
                return True  # Comment added successfully
            else:
                logger.warning(f"JIRA Failed to add comment: {response.status_code} - {response.text}")
                raise Exception(f"JIRA Failed to add comment: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"JIRA Error while adding comment: {str(e)}")
            raise Exception(f"JIRA Error while adding comment: {str(e)}")

    def update_issue(self, issue_key, update_data):
        endpoint = f"{self.base_url}/issue/{issue_key}"
        headers = {"Content-Type": "application/json"}
        response = requests.put(endpoint, json=update_data, headers=headers, auth=self.auth)

        if response.status_code == 204:
            logger.info("Updated ticket: " + issue_key)
            return True
        else:
            logger.warning(f"JIRA Failed to update issue: {response.status_code} - {response.text}")
            raise Exception(f"JIRA Failed to update issue: {response.status_code} - {response.text}")
        
    
    def get_issue_status(self, issue_key):
        endpoint = f"{self.base_url}/issue/{issue_key}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.get(endpoint, headers=headers, auth=self.auth)

            if response.status_code == 200:
                issue_data = response.json()
                status = issue_data["fields"]["status"]["name"]
                return status
            else:
                logging.warning(f"JIRA Failed to get issue status: {response.status_code} - {response.text}")
                raise Exception(f"JIRA Failed to get issue status: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"JIRA Error while getting issue status: {str(e)}")
            raise Exception(f"JIRA Error while getting issue status: {str(e)}")
        
    def get_transition_id_for_status(self, issue_key, desired_status):
        endpoint = f"{self.base_url}/issue/{issue_key}/transitions"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.get(endpoint, headers=headers, auth=self.auth)

            if response.status_code == 200:
                transitions_data = response.json()["transitions"]
                for transition in transitions_data:
                    if transition["to"]["name"] == desired_status:
                        return transition["id"]
                # If the desired status transition was not found
                logger.error(f"JIRA Desired status transition '{desired_status}' not found.")
                raise Exception(f"JIRA Desired status transition '{desired_status}' not found.")
            else:
                logger.error(f"JIRA Failed to get available transitions: {response.status_code} - {response.text}")
                raise Exception(f"JIRA Failed to get available transitions: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"JIRA Error while getting transition ID: {str(e)}")   
            raise Exception(f"JIRA Error while getting transition ID: {str(e)}")   
        
    def transition_issue_with_comment(self, issue_key, transition_id, comment_body):
        transition_data = {
            "transition": {"id": transition_id},
            "update": {
                "comment": [{"add": {"body": comment_body}}]
            }
        }
        transition_endpoint = f"{self.base_url}/issue/{issue_key}/transitions"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(transition_endpoint, json=transition_data, headers=headers, auth=self.auth)

            if response.status_code == 204:
                return True  # Issue successfully transitioned with a comment
            else:
                logger.error(f"JIRA Failed to transition issue with comment: {response.status_code} - {response.text}")
                raise Exception(f"JIRA Failed to transition issue with comment: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"JIRA Error while transitioning issue with comment: {str(e)}")
            raise Exception(f"JIRA Error while transitioning issue with comment: {str(e)}")
    
    def transition_issue(self, issue_key, transition_id):
        transition_data = {
            "transition": {"id": transition_id},
            "fields": {
                "assignee": {"name": settings.JIRA_USERNAME}
            }
        }
        transition_endpoint = f"{self.base_url}/issue/{issue_key}/transitions"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(transition_endpoint, json=transition_data, headers=headers, auth=self.auth)

            if response.status_code == 204:
                return True  # Issue successfully transitioned
            else:
                logger.error(f"JIRA Failed to transition issue: {response.status_code} - {response.text}")
                raise Exception(f"JIRA Failed to transition issue: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"JIRA Error while transitioning issue: {str(e)}")
            raise Exception(f"JIRA Error while transitioning issue: {str(e)}")
    
    def close_issue(self, issue_key):
        transition_id = self._get_close_transition_id(issue_key)
        if transition_id:
            data = {"transition": {"id": transition_id}}
            endpoint = f"{self.base_url}/issue/{issue_key}/transitions"
            headers = {"Content-Type": "application/json"}
            response = requests.post(endpoint, json=data, headers=headers, auth=self.auth)

            if response.status_code == 204:
                return True
            else:
                logger.error(f"JIRA Failed to close issue: {response.status_code} - {response.text}")
                raise Exception(f"JIRA Failed to close issue: {response.status_code} - {response.text}")
        else:
            logger.error("JIRA Close transition not found")
            raise Exception("JIRA Close transition not found")

    def _get_close_transition_id(self, issue_key):
        endpoint = f"{self.base_url}/issue/{issue_key}/transitions"
        response = requests.get(endpoint, auth=self.auth)

        if response.status_code == 200:
            transitions = response.json()["transitions"]
            for transition in transitions:
                if transition["to"]["name"].lower() == "closed":
                    return transition["id"]
        return None
    

def createJira(desc, area, requestor, approvers):
    jira_service = JiraService()
    if "YOULAB" in area.name:
        areaSimple = "YOULAB"
        requestType = "Youlab Support Request"
    
    if "WELAB" in area.name:
        areaSimple = "WELAB"
        requestType = "Welab Support Request"
    
    if "APPLICATION SERVICES" in area.name:
        areaSimple = "APPLICATION SERVICES"
        requestType = "Application Service Request"

    if "LEARNING SERVICES" in area.name:
        areaSimple = "LEARNING  SERVICES"
        requestType = "Application Service Request"

    participants_list = [{"name": requestor}]    

    for approver in approvers:
        participants_list.append({"name": approver})


    issue_data = {
        "fields": {
            "project":{"key": "GTEC"},
            "issuetype":{"name": "Service Request"},
            "summary":"[AMS] Account Request"+" "+ area.name,
            "description":desc,
            "customfield_19090":{"value":areaSimple},
            "customfield_13812":requestType,
            "customfield_12613":[{"value":"NM"}],
            "customfield_20045":participants_list,
            "customfield_18013":{"value":"BNEW DNEW DPS"},
        }
    }
    #print(issue_data)
    try:
        created_issue = jira_service.create_issue(issue_data)
            # Handle the response or redirect to a success page.
        return created_issue.get("key")
    except Exception as e:
            # Handle the 
        error_message = f"Failed to create issue: {str(e)}"
        raise Exception( error_message)

def putJiraInProgress(ticket_number):
    jira_service = JiraService()
    
    try:
        current_status = jira_service.get_issue_status(ticket_number)
        
        # Check if the issue is already in progress
        if current_status == "In Progress":
            return "Already in Progress"
        jira_service.transition_issue(ticket_number, jira_service.get_transition_id_for_status(ticket_number, "In Progress"))
        return "OK"
    except Exception as e:
            # Handle the 
        error_message = f"Failed to put in progress issue: {str(e)}"
        raise Exception( error_message)

def commentJira(ticket_number,comment):
    jira_service = JiraService()
    try:
            jira_service.add_comment(ticket_number, comment)
            # Handle the response or redirect to a success page.
            return "OK"
    except Exception as e:
            # Handle the 
            error_message = f"Failed to comment issue: {str(e)}"
            raise Exception( error_message)
    


def closeJira(ticket_number,comment,status):
    jira_service = JiraService()
    try:
        jira_service.transition_issue_with_comment(ticket_number, jira_service.get_transition_id_for_status(ticket_number, status), comment)
        #Uncomment when ready to close tikcet after resolving all orders
        jira_service.close_issue(ticket_number)
        return "OK"
    except Exception as e:
            # Handle the 
        error_message = f"Failed to close issue: {str(e)}"
        raise Exception( error_message)
                
 