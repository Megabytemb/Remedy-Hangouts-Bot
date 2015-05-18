import requests
import xmltodict
import json

CONFIG = json.load(open("config.json"))

def get_incident(Incident_Number):
    url=CONFIG["incident_service"]
    #headers = {'content-type': 'application/soap+xml'}
    headers = {'content-type': 'text/xml',
                'SOAPAction': 'urn:HPD_IncidentInterface_WS/HelpDesk_Query_Service'}
    body = """<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
        <Header>
            <AuthenticationInfo xmlns="urn:HPD_IncidentInterface_WS">
                <userName>{1}</userName>
                <password>{2}</password>
            </AuthenticationInfo>
        </Header>
        <Body>
            <HelpDesk_Query_Service xmlns="urn:HPD_IncidentInterface_WS">
                <Incident_Number>{0}</Incident_Number>
            </HelpDesk_Query_Service>
        </Body>
    </Envelope>""".format(Incident_Number,CONFIG["remedy_username"],CONFIG["remedy_password"])

    response = requests.post(url,data=body,headers=headers)
    r = response.text.replace("ns0:","")

    xml = xmltodict.parse(r)
    incident = xml['soapenv:Envelope']['soapenv:Body']['HelpDesk_Query_ServiceResponse']
    return incident

def nice_state(incident):
    state = incident["Status"]
    if state == "Assigned":
        return "is currently assigned to"
    if state == "In Progress":
        return "is currently in progress with"
    if state == "Pending":
        return "is currently pending with"
    if state in ("Resolved", "Closed", "Cancelled"):
        return "was Resolved by"
    
def nice_support_group_and_person(incident):
    if incident["Assignee"] != None:
        return "{0} in {1}".format(incident["Assignee"], incident["Assigned_Group"])
    return incident["Assigned_Group"]

def parse_incident(incident):
    try:
       incident = get_incident(incident)
    except:
       return "That incident doesn't exist. Sorry"
    template = "That Incident for {0} {1} {2} {3}"
    return template.format(incident["First_Name"], 
                           incident["Last_Name"], 
                           nice_state(incident), 
                           nice_support_group_and_person(incident)
                           )
