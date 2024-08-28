import logging
from jira import JIRA

def booking_details_comment(jira_id,team,
                            pm,start_date,
                            end_date,cluster_name,
                            namespace,fqdn,
                            eic_version,reporter,
                            ip):
    comment = f"""
    Hi [~{reporter}] ,

    Please find booking details below:



    *Booking Details:*
    |*Booking Details*|*Information*|
    |*Ticket Number*|{jira_id}|
    |*Program*|Aeonic|
    |*Team*|Team {team}|
    |*Project Manager*|{pm}|
    |*Start Date*|{start_date}|
    |*Timebox End Date*|{end_date}|
    |*Cluster Name & EWS Link*|[{cluster_name}|https://ews.rnd.gic.ericsson.se/cd.php?cluster={cluster_name}]|
    |*Namespace*|{namespace}|
    |*Domain*|*{fqdn}|
    |*IP*|{ip}|
    |*EIC Version Installed*|{eic_version}|
    |*Grafana Dashboard*|[CCD Resource allocation - Tools - Dashboards - Grafana (ericsson.se)|https://monitoring1.stsoss.seli.gic.ericsson.se:3000/d/BtVVluP7k/ccd-resource-allocation?orgId=1&var-dc=ews0&var-vpod=EIAP&var-program=DETS&var-cluster_id={cluster_name}&var-Namespace=All&var-pod=All]|
    |*Log Viewer*|gas{fqdn}|
    """
    return comment

LOG = logging.getLogger(__name__)

class PoolJira():
    def __init__(self, jira_id):
        self.jira_host = values.JIRA_URL
        self.jira_pat = values.JIRA_PAT_TOKEN
        self.jira_id = jira_id
    
    def getJiraConnection(self):
        LOG.debug("Creating the jira client")

        jira_client = JIRA(server = self.jira_host, token_auth = self.jira_pat)
        return jira_client

    def __get_jira_client_and_issue(self):
        jira = self.getJiraConnection()
        return jira, jira.issue(self.jira_id)

    def __get_valid_transitions(self):
        jira, issue = self.__get_jira_client_and_issue()
        return [(transition['id'], transition['name']) for transition in jira.transitions(issue)]

    def add_comment(self, comment: str):
        jira, issue = self.__get_jira_client_and_issue()
        jira.add_comment(issue, comment)

    def add_remote_link(self, remote_link: str):
        jira, issue = self.__get_jira_client_and_issue()
        jira.add_remote_link(issue, {"url": remote_link, "title": remote_link})

    def add_attachment(self, path_to_attachment: str):
        jira, issue = self.__get_jira_client_and_issue()
        jira.add_attachment(issue=issue, attachment=path_to_attachment)

    def add_jenkins_attachment(self, jenkins_build_url: str, artifact_name: str):
        jira, issue = self.__get_jira_client_and_issue()
        # download build artifact from Jenkins job
        # TBD
        jira.add_attachment(issue=issue, attachment=artifact_name)

    def add_watchers(self, watchers: str): 
        jira, issue = self.__get_jira_client_and_issue()
        [jira.add_watcher(issue, watcher) for watcher in watchers.split(',')]

    def transition_to(self, transition_to: str):
        jira, issue = self.__get_jira_client_and_issue()
        valid_transitions = self.__get_valid_transitions()
        LOG.info(f"Valid transitions are {valid_transitions}")
        [jira.transition_issue(issue, transition_id) for transition_id, transition_name in valid_transitions if transition_name.lower() in transition_to.lower()]
    
    # def create_new_jira(self, fields: dict):
    #     jira = getJiraConnection(self)



