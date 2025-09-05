import requests
import re
from datetime import datetime, UTC, timedelta
from enum import Enum
import time
from playwright.sync_api import sync_playwright

class ReferenceType(Enum):
    BOOK_OF_MORMON = 23,
    MISSIONARY_VISIT = 134

class ReferralManager:

    def __init__(self, username: str, password: str, email: str, mission_id: int):
        """
        :param str username: username of the referral manager user
        :param str password: password of the referral manager user
        :param str email: media secretary email
        :param int mission_id: id of the mission
        """
        self.__session = requests.session()
        self.__username = username
        self.__password = password
        self.__mission_id = mission_id
        self.__authenticate()
        self.__media_sec = self.__get_media_sec_info(email, mission_id)

    def __host(self, name: str) -> str:
        return f"https://{name}.churchofjesuschrist.org"
    
    def __authenticate(self):
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()

        # Go to login page
        page.goto(f"{self.__host('www')}/services/platform/v4/login",
                  wait_until="networkidle",
                  timeout=15000)

        # Fill username and submit
        page.locator("input:visible").first.fill(self.__username)
        page.keyboard.press("Enter")

        # Fill password and submit
        page.locator("input[type='password']:visible").first.fill(self.__password)
        page.keyboard.press("Enter")
        page.wait_for_url(f"{self.__host('www')}/**")

        #Warm up and collect cookies from referralmanager
        all_cookies = []

        page.goto(self.__host("referralmanager"), wait_until="load")
        page.wait_for_url(self.__host("referralmanager"))
        all_cookies.extend(ctx.cookies())

        unique_cookies = {(c["name"], c["domain"]): c for c in all_cookies}.values()

        access_token = next(
            c["value"] for c in unique_cookies if c["name"] == "oauth_id_token"
        )

        for c in unique_cookies:
            self.__session.cookies.set(
                c["name"], c["value"], domain=c["domain"].lstrip(".")
            )

        # Close Playwright
        browser.close()
        p.stop()

        self.__session.cookies.set("owp", access_token)

        
        # html_resp = self.__session.get(f"{self.__host('www')}/services/platform/v4/login").content.decode("unicode_escape")
        # state_token = re.search(r"\"stateToken\":\"([^\"]+)\"", html_resp).groups()[0]
        # self.__session.post(f"{self.__host('id')}/idp/idx/introspect")#, json={"stateToken": state_token})
        # username_res = self.__session.post(f"{self.__host('id')}/idp/idx/identify", json={"identifier": self.__username, "stateHandle": state_token}).json()
        # state_handle = username_res["stateHandle"]
        # password_auth_id = [auth_type["id"] for auth_type in username_res["authenticators"]["value"] if auth_type["type"] == "password"][0]
        # authenticators_resp = self.__session.post(f"{self.__host('id')}/idp/idx/challenge", json={
        #     "authenticator": {
        #         "id": password_auth_id,  # Password authenticator ID
        #         "methodType": "password"
        #     },
        #     "stateHandle": state_handle
        # }).json()
        # state_handle = authenticators_resp["stateHandle"]
        # challenge_resp = self.__session.post(f"{self.__host('id')}/idp/idx/challenge/answer", json={
        #     "credentials": {"passcode": self.__password}, 
        #     "stateHandle": state_handle
        # }).json()
        # self.__session.get(challenge_resp["success"]["href"])
        # access_token = self.__session.cookies.get_dict()["oauth_id_token"]
        # self.__session.cookies.set("owp", access_token)
    
    def __get_media_sec_info(self, email: str, mission_id: int) -> dict:
        mission = self.get_mission_info()
        for zone in mission['children']:
            for district in zone['children']:
                for area in district['children']:
                    for missionary in area['missionaries'] if area['missionaries'] else []:
                        if missionary['emailAddress'] == email:
                            return missionary
        return None
    
    def get_mission_id(self) -> int:
        mission_id = self.__session.get(self.__host('referralmanager') + '/services/people/mission').json()['persons'][0]['missionId']
        return mission_id
    
    def get_mission_info(self) -> dict:
        mission = self.__session.get(self.__host('referralmanager') + f'/services/mission/{self.__mission_id}').json()['mission']
        return mission
    
    def get_area_for_address(self, address: str):
        designated_area = self.__session.get(self.__host('referralmanager') + f'/services/mission/assignment', params={'address': address, 'langCd': 'por'}).json()
        return designated_area
    
    def get_area_for_location(self, coords: dict[float]):
        designated_area = self.__session.get(self.__host('referralmanager') + f'/services/mission/assignment', params={'coordinates': str(coords[0]) + ',' + str(coords[1]), 'langCd': 'por'}).json()
        return designated_area
    
    def create_and_send_reference(self, first_name: str, last_name: str, address: str, phone: str, email: str, reference_type: ReferenceType, referral_note: str):
        """
        :param str first_name: First name of the reference
        :param str last_name: Last name of the reference
        :param str address: Address of the reference
        :param str phone: Phone number of the reference
        :param str email: Email address of the reference
        :param ReferenceType reference_type: Type of reference solicited
        :param str referral_note: Note that the missionaries will receive about the reference
        """
        designated_area = self.get_area_for_address(address)
        org_id = designated_area["bestOrgId"]
        pros_area_id = designated_area["bestProsAreaId"]

        data = {
            "payload": {
                "offers": [
                    {
                        "personGuid": None,
                        "offerItemId": reference_type.value, # 23 is book of mormon reference, 134 visita dos missionarios
                        "deliveryMethodId": 1 # in person delivery
                    }
                ],
                "referral": {
                    "personGuid": None,
                    "referralNote": referral_note, # referal note to be included with the reference
                    "createDate": int(datetime.now(UTC).timestamp() * 1000),
                    "sentToLocalPersonGuid": self.__media_sec["clientGuid"],
                    "sentToLocalAppId": None,
                    "referralStatus": "UNCONTACTED" # the reference has been uncontacted
                },
                "household": {
                    "stewardCmisId": None,
                    "address": address, # address of the reference
                    "lat": None, # if there should be specific latitude information, if not the system will automatically create the pin
                    "lng": None, # if there should be specific longditude information, if not the system will automatically create the pin
                    "pinDropped": None, # if there was a specific pin location specified
                    "locId": 87, # Brazil location ID
                    "orgId": org_id, # ID of the closest ward or branch
                    "missionaryId": None,
                    "modDate": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M.%S0Z"), # time of creation,
                    "people": [
                        {
                            "firstName": first_name, # first name of the reference
                            "lastName": last_name, # last name of the reference
                            "contactSource": 15398, # found through mission media page
                            "preferredLangId": 59, # perfered language portugues
                            "ageCatId": None,
                            "preferredContactType": None,
                            "preferredPhoneType": "PHN_MOBILE", # sets mobile phone as the default contact method
                            "preferredEmailType": "EMAIL_HOME",
                            "gender": None,
                            "note": "",
                            "tags":[],
                            "foundByPersonGuid": None,
                            "contactInfo": {
                                "phoneNumbers": [
                                    {
                                        "type": "PHN_MOBILE",
                                        "number": phone,
                                        "textable": True
                                    }
                                ],
                                "emailAddresses": [
                                    {
                                        "type": "EMAIL_HOME",
                                        "address": email
                                    }
                                ]
                            },
                            "status": 1,
                            "dropNotes": None,
                            "prosAreaId": pros_area_id,
                            "changerId": self.__media_sec["cmisId"]
                        }
                    ],
                "changerId": self.__media_sec["cmisId"],
            },
            "person": {
                "firstName": first_name, # first name of the reference
                "lastName": last_name, # last name of the reference
                "contactSource": 15398, # this person was found through mission media page
                "preferredLangId": 59, # perfered language portugues
                "ageCatId": None,
                "preferredContactType": None,
                "preferredPhoneType": "PHN_MOBILE", # sets mobile phone as the default contact method
                "preferredEmailType": "EMAIL_HOME",
                "gender": None,
                "note": "",
                "tags":[],
                "foundByPersonGuid": None,
                "contactInfo": {
                    "phoneNumbers": [
                        {
                            "type": "PHN_MOBILE",
                            "number": phone,
                            "textable": True
                        }
                    ],
                    "emailAddresses": [
                        {
                            "type": "EMAIL_HOME",
                            "address": email
                        }
                    ]
                },
                "status": 1,
                "dropNotes": None,
                "prosAreaId": pros_area_id
            },
            "follow": [
                self.__media_sec["cmisId"]
            ],
            "needsPrivacyNotice": True
            }
        }
        resp = self.__session.post(f"{self.__host("referralmanager")}/services/referrals/sendtolocal", json=data)
        return resp
    
    def assign_referrals(self):
        unassigned_people = self.get_unassigned_people()
        print(f'Tentando designar {len(unassigned_people)} pessoas...')
        for person in unassigned_people:
            try:
                designated_area = self.get_area_for_address(person['address'])
                if designated_area['bestProsAreaId'] == None:
                    designated_area = self.get_area_for_location(designated_area['coordinates'])
                    if designated_area['bestProsAreaId'] == None:
                        continue
                household = self.__session.get(self.__host('referralmanager') + '/services/households/' + person['householdGuid']).json()
                household['people'][0]['prosAreaId'] = designated_area['bestProsAreaId']
                household['orgId'] = designated_area['bestOrgId']
                household['modDate'] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
                household['people'][0]['changerId'] = self.__media_sec["cmisId"]
                household['missionaryId'] = None
                household['changerId'] = self.__media_sec["cmisId"]
                household['people'][0]['householdInfo'] = {
                    "orgId": designated_area['missions'][0]['orgId'],
                    "orgNum": household['orgNum'],
                    "stewardCmisId": None,
                    "address": household['address'],
                    "locId": household['locId']
                }

                data = {
                    "payload": {
                        "offers": [],
                        "referral": {
                            "personGuid": None,
                            "referralNote": None,
                            "createDate": int(datetime.now(UTC).timestamp() * 1000),
                            "sentToLocalPersonGuid": self.__media_sec["clientGuid"],
                            "sentToLocalAppId": None,
                            "referralStatus": "UNCONTACTED"
                        },
                        "household": household,
                        "person": household['people'][0].copy(),
                        "follow": [self.__media_sec["cmisId"]],
                        "needsPrivacyNotice": False
                    }
                }
                data['payload']['person'].pop('changerId')
                res = self.__session.post(f"{self.__host("referralmanager")}/services/referrals/sendtolocal", json=data)
                status_code = res.status_code
                if status_code != 200:
                    print(f'Erro ao designar {person["firstName"]} {person["lastName"]} para a area {designated_area["bestProsAreaId"]}. response: {res.status_code} - {res.reason}')
                    continue
                print(f'Designou {person['firstName']} com successo!')
            except:
                continue

    def get_all_references(self) -> list:
        return self.__session.get(self.__host("referralmanager") + f"/services/people/mission/{self.__mission_id}").json()['persons']

    def get_unassigned_people(self) -> list:
        people = self.get_all_references()
        return [person for person in people if person['areaId'] is None]
    
    def get_recent_converts(self) -> list:
        people = self.get_all_references()
        return [person for person in people if person['convert'] == True]
    
    def get_person(self, guid: int):
        return self.__session.get(f'{self.__host('referralmanager')}/services/people/{guid}').json()
    
    def get_household(self, guid: int):
        return self.__session.get(f'{self.__host('referralmanager')}/services/households/{guid}').json()
    
    def get_references_by_area_name(self, area_name: str):
        references = self.get_all_references()
        return [reference for reference in references if reference['areaName'] == area_name]

    def get_references_by_district_name(self, district_name: str):
        references = self.get_all_references()
        return [reference for reference in references if reference['districtName'] == district_name]

    def get_references_by_zone_name(self,zone_name: str):
        references = self.get_all_references()
        return [reference for reference in references if reference['zoneName'] == zone_name]
    
    def stop_teaching_for_far_from_cof(self, guid: int):
        return self.__session.put(self.__host("referralmanager") + f"/services/people/{guid}/drop", json={"status": 28})
    
    def get_timeline(self, person_id: str):
        return self.__session.get(self.__host("referralmanager") + f"/services/progress/timeline/{person_id}").json()

