import re
import util
import remedy

match_incident = re.compile(r'\bINC000000[0-9]{6,6}\b', re.IGNORECASE)
match_small_incident = re.compile(r'\bINC[0-9]{6,6}\b', re.IGNORECASE)
match_long_incident = re.compile(r'(incident|inc)( (number|no))? [0-9]{6,6}', re.IGNORECASE)

def short_to_long(incident):
	return "inc000000"+incident[3:]

def add_inc_short(incident):
   return "inc000000" + incident

def get_message_to_all(sanitised_message):
    incident = match_incident.search(sanitised_message)
    small_incident = match_small_incident.search(sanitised_message)
    long_incident = match_long_incident.search(sanitised_message)
    if incident is not None:
        return remedy.parse_incident(incident.group())
    if small_incident is not None:
        incident = short_to_long(small_incident.group())
        return remedy.parse_incident(incident)
    if long_incident is not None:
        incident = add_inc_short(long_incident.group().split()[1])
        return remedy.parse_incident(incident)
    return

def get_message_to_me(sanitised_message):
    return "something"
    
