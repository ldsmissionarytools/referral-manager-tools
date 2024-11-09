from ReferralManager import ReferralManager
import re
import csv
import json
from pathlib import Path

with open(Path(__file__).with_name('settings.json')) as f:
    try:
        settings = json.load(f)
    except:
        settings = dict()
        settings['username'] = ''
        settings['password'] = ''
        settings['sec_email'] = ''
        settings['mission_id'] = 0
    

    username = settings['username']
    password = value=settings['password']
    sec_email = value=settings['sec_email']
    mission_id = value=settings['mission_id']

referral_manager = ReferralManager(username,password, sec_email, mission_id)

recent_converts = referral_manager.get_recent_converts()

with open('recent_converts.csv', mode='w', newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Address'])

    for convert in recent_converts:
        household = referral_manager.get_household(convert['householdGuid'])
        for person in household['people']:
            contact_info = person['contactInfo']
            if contact_info != None:
                info = [person['firstName'], person['lastName']]
                
                if contact_info['emailAddresses'] != None:
                    info.append(contact_info['emailAddresses'][0]['address'])
                else:
                    info.append(None)
                if contact_info['phoneNumbers'] != None and int(re.sub('[^A-Za-z0-9]+', '', str(contact_info['phoneNumbers'][0]['number']))) > 99:
                    info.append(contact_info['phoneNumbers'][0]['number'])
                else:
                    info.append(None)
                
                info.append(household['address'])
                writer.writerow(info)

print('Done')