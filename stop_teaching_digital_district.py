from ReferralManager import ReferralManager, ReferenceType
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

DISTRICT_NAME = 'Digital'

referral_manager: ReferralManager = ReferralManager(username, password, sec_email, mission_id)

referrals = referral_manager.get_references_by_district_name(DISTRICT_NAME)
# referrals = referral_manager.get_references_by_area_name(AREA_NAME)

for referral in referrals:
    #if the person is a yellow point
    if (referral['personStatusId'] == 1):
        referral_manager.stop_teaching_for_far_from_cof(referral['personGuid'])
        print("Stopped teaching " + str(referral['firstName']) + " sucessfully")

print('Done')
