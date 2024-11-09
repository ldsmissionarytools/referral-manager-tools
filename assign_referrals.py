from __future__ import annotations
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

def assign_referrals(referral_manager: ReferralManager):
    referral_manager.assign_referrals()
    print('Finished sucessfully')

referral_manager: ReferralManager = ReferralManager(username, password, sec_email, mission_id)
assign_referrals(referral_manager)
# referral_manager.create_and_send_reference(first_name="Elizama Roza Dias", last_name="", address="Rua marques de abrantes 355, Novo Hamburgo, RS", phone="5551992343896", email="elizama.roza@hotmail.com", reference_type=ReferenceType.BOOK_OF_MORMON, referral_note="Esse Livro é de Graça - Sister Baker")

# get a list of all the references test = session.get(host('referralmanager') + "/services/people/mission").content