from ReferralManager import ReferralManager, ReferenceType
import json
from pathlib import Path

with open(Path(__file__).with_name('settings.json')) as f:
    settings = json.load(f)
    

    username = settings['username']
    password = value=settings['password']
    sec_email = value=settings['sec_email']
    mission_id = value=settings['mission_id']

referral_manager: ReferralManager = ReferralManager(username, password, sec_email, mission_id)

mission = referral_manager.get_mission_info()

mission_zones = dict()

zones = mission['children']

for zone in zones:
    mission_zones[zone['name']] = []
    districts = zone['children']
    for district in districts:
        areas = district['children']
        for area in areas:
            area_name = area['name']
            mission_zones[zone['name']].append(area_name)

print(mission_zones)