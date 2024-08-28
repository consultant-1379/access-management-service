# This file contains constants
JENKINS_URL = "https://jenkins1.stsoss.seli.gic.ericsson.se:8080"
TEARDOWN_JOB = "EIAP_deploy_teardown"
CRD_NAMESPACE = 'eric-crd-ns'
EIC_EASY_TRIGGER_JOB= "EIAP_deploy_MASTER_PIPELINE__easy_trigger"
MANAGE_BOOKINGS_JOB= "KaaS_manage_BOOKINGS"
JENKINS_USERNAME = "eforgav"
JENKINS_TOKEN = "11a9df5ec4dba26748767748102819f911"
# JENKINS_USERNAME = "DETSUSER"
# JENKINS_TOKEN = "XIawIYW0yr-c2bxkBQBGtUUoz"
PROMETHEUS_URI= "http://10.117.246.164:9099"
SPINNAKER_URL = 'https://spinnaker-api.rnd.gic.ericsson.se/webhooks/webhook/eic-pooled-deployment-initial-install-pipeline-v3'

# Jira Config for Pool Test Environments
# JIRA_URL                            = "https://jira-oss.seli.wh.rnd.internal.ericsson.com"
# JIRA_TEMPLATE                       = f"{JIRA_URL}/browse/dets-8320"
JIRA_URL                            = "https://eteamproject.internal.ericsson.com/"
JIRA_PAT_TOKEN                      = "NTA1OTMwOTU2MjA3OksseTrslKDkW20nqqLE/a+af1+A"

# Some of the jira messages for pool Environments
BOOKING_TICKET_DESCRIPTION_TEMPLATE = ""
POOL_GRAFANA_URL = "https://monitoring1.stsoss.seli.gic.ericsson.se:3000/d/BtVVluP7k/ccd-resource-allocation?orgId=1&var-dc=ews0&var-vpod=EIAP&var-program=DETS&var-cluster_id={cluster_name}&var-Namespace={namespace}&var-pod=All"


