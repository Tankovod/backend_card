import time
import uuid

import aiohttp
import jwt

from card.s3 import ImageData


class Apple:
    def __init__(self):
        self.api_url = 'https://api.pub1.passkit.io/'
        self.api_key = '0WegrJ6AfSnuipINFHEFjS'
        self.api_secret = 'w+VZziqpaPFt560+SMF5NAYUY2txVMtLJaNsXVqk'

    async def auth(self):
        jwt_body = {
            "uid": self.api_key,
            "exp": int(time.time()) + 60,  # Expiry time (in 10 minutes)
            "iat": int(time.time())
        }

        token = jwt.encode(
            jwt_body,
            self.api_secret,
            algorithm='HS256'
        )

        header = {
            'Authorization': f"Bearer {token}",
            "Content-type": "application/json"
        }
        return header

    async def upload_image(self, url_logo, url_background, url_icon):
        logo = ImageData(url_logo)
        image_logo = await logo.crop_and_upload_image((660, 660))
        background = ImageData(url_background)
        image_background = await background.crop_and_upload_image((1032, 336))
        icons = ImageData(url_icon)
        icon = await icons.crop_and_upload_image((114, 114))
        strips = ImageData(url_background)
        strip = await strips.crop_and_upload_image((1125, 432))

        headers = await self.auth()
        image_id = str(uuid.uuid4())
        body = {
            "name": image_id.replace('-', ''),
            "imageData": {
                "icon": f"{icon}",
                "logo": f"{image_logo}",
                "appleLogo": f"{image_logo}",
                "hero": f"{image_background}",
                "strip": f"{strip}"
            },
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.api_url + 'images', json=body, headers=headers) as response:
                data = await response.json()
                print(data)
                return data

    async def create_full_card(self, **kwargs):
        header = await self.auth()
        try:
            try:
                img = await self.upload_image(kwargs['logo'], kwargs['background'], kwargs['icon_push'])
                print(img)
            except Exception as error:
                img = {
                    'logo': '2Q6pr00l8z0kQsoJuKofkf',
                    'appleLogo': '3YPgmVdbvf30X4AUeH89Cv',
                    'background': '1S1u6zIyCjTvAHPTNsQt5U'
                }
                print('Images were broken: ', error)

            body_par = {
                'name': kwargs['corp_name'],
                "localizedName": None,
                'status': ["PROJECT_ACTIVE_FOR_OBJECT_CREATION", "PROJECT_DRAFT"],
                'quota': None
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url=self.api_url + "members/program", json=body_par, headers=header) as app:
                    app_id = (await app.json())['id']
                    body = {
                        "name": kwargs['corp_name'],
                        "protocol": "MEMBERSHIP",
                        "revision": 1,
                        "defaultLanguage": "RU",
                        "organizationName": f"{kwargs['corp_name']}",
                        "localizedOrganizationName": None,
                        "description": "Your special card",
                        "localizedDescription": None,
                        "data": {
                            "dataFields": [
                                {
                                    "uniqueName": "members.program.name",
                                    "templateId": "",
                                    "fieldType": "PROTOCOL_FIELDS",
                                    "label": "",
                                    "localizedLabel": None,
                                    "dataType": "TEXT",
                                    "defaultValue": "Loyalty",
                                    "localizedDefaultValue": None,
                                    "validation": "",
                                    "currencyCode": "",
                                    "appleWalletFieldRenderOptions": {
                                        "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                        "positionSettings": {
                                            "section": "FIELD_SECTION_DO_NOT_USE",
                                            "priority": 0
                                        },
                                        "changeMessage": "",
                                        "localizedChangeMessage": None,
                                        "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                        "suppressLinkDetection": [],
                                    },
                                    "dataCollectionFieldRenderOptions": {
                                        "helpText": "",
                                        "localizedHelpText": None,
                                        "displayOrder": 0,
                                        "placeholder": "",
                                        "selectOptions": [],
                                        "localizedPlaceholder": None,
                                        "addressRenderOptions": None,
                                        "localizedYearPlaceholder": "",
                                        "localizedMonthPlaceholder": "",
                                        "localizedDayPlaceholder": ""
                                    },
                                    "usage": [
                                        "USAGE_GOOGLE_PAY"
                                    ],
                                    "googlePayFieldRenderOptions": {
                                        "googlePayPosition": "GOOGLE_PAY_LOYALTY_PROGRAM_NAME",
                                        "textModulePriority": 0
                                    },
                                    "defaultTelCountryCode": ""
                                },
                                {
                                    "uniqueName": "members.member.points",
                                    "templateId": "",
                                    "fieldType": "PROTOCOL_FIELDS",
                                    "label": f"{kwargs['top_header']}",
                                    "localizedLabel": None,
                                    "dataType": "TEXT",
                                    "defaultValue": f"{kwargs['top_body']}",
                                    "localizedDefaultValue": None,
                                    "validation": "",
                                    "currencyCode": "",
                                    "appleWalletFieldRenderOptions": {
                                        "textAlignment": "RIGHT",
                                        "positionSettings": {
                                            "section": "HEADER_FIELDS",
                                            "priority": 0
                                        },
                                        "changeMessage": "You now have %@ points!",
                                        "localizedChangeMessage": None,
                                        "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                        "suppressLinkDetection": [],
                                    },
                                    "dataCollectionFieldRenderOptions": {
                                        "helpText": "",
                                        "localizedHelpText": None,
                                        "displayOrder": 0,
                                        "placeholder": "",
                                        "selectOptions": [],
                                        "localizedPlaceholder": None,
                                        "addressRenderOptions": None,
                                        "localizedYearPlaceholder": "",
                                        "localizedMonthPlaceholder": "",
                                        "localizedDayPlaceholder": ""
                                    },
                                    "usage": [
                                        "USAGE_APPLE_WALLET"
                                    ],
                                    "googlePayFieldRenderOptions": {
                                        "googlePayPosition": "GOOGLE_PAY_LOYALTY_POINTS",
                                        "textModulePriority": 0
                                    },
                                    "defaultTelCountryCode": ""
                                },
                                {
                                    "uniqueName": "person.displayName",
                                    "templateId": "",
                                    "fieldType": "PII",
                                    "label": f"{kwargs['left_header']}",
                                    "localizedLabel": None,
                                    "dataType": "TEXT",
                                    "defaultValue": f"{kwargs['left_body']}",
                                    "localizedDefaultValue": None,
                                    "validation": "",
                                    "currencyCode": "",
                                    "appleWalletFieldRenderOptions": {
                                        "textAlignment": "LEFT",
                                        "positionSettings": {
                                            "section": "SECONDARY_FIELDS",
                                            "priority": 0
                                        },
                                        "changeMessage": "",
                                        "localizedChangeMessage": None,
                                        "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                        "suppressLinkDetection": [],
                                    },
                                    "dataCollectionFieldRenderOptions": {
                                        "helpText": "",
                                        "localizedHelpText": None,
                                        "displayOrder": 0,
                                        "placeholder": "",
                                        "selectOptions": [],
                                        "localizedPlaceholder": None,
                                        "addressRenderOptions": None,
                                        "localizedYearPlaceholder": "",
                                        "localizedMonthPlaceholder": "",
                                        "localizedDayPlaceholder": ""
                                    },
                                    "usage": [
                                        "USAGE_APPLE_WALLET",
                                        "USAGE_GOOGLE_PAY",
                                        "USAGE_DATA_COLLECTION_PAGE"
                                    ],
                                    "googlePayFieldRenderOptions": {
                                        "googlePayPosition": "GOOGLE_PAY_LOYALTY_ACCOUNT_NAME",
                                        "textModulePriority": 0
                                    },
                                    "defaultTelCountryCode": ""
                                },
                                {
                                    "uniqueName": "members.tier.name",
                                    "templateId": "",
                                    "fieldType": "PROTOCOL_FIELDS",
                                    "label": f"{kwargs['right_header']}",
                                    "localizedLabel": None,
                                    "dataType": "TEXT",
                                    "defaultValue": f"{kwargs['right_body']}",
                                    "localizedDefaultValue": None,
                                    "validation": "",
                                    "currencyCode": "",
                                    "appleWalletFieldRenderOptions": {
                                        "textAlignment": "RIGHT",
                                        "positionSettings": {
                                            "section": "SECONDARY_FIELDS",
                                            "priority": 1
                                        },
                                        "changeMessage": "",
                                        "localizedChangeMessage": None,
                                        "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                        "suppressLinkDetection": [],
                                    },
                                    "dataCollectionFieldRenderOptions": {
                                        "helpText": "",
                                        "localizedHelpText": None,
                                        "displayOrder": 0,
                                        "placeholder": "",
                                        "selectOptions": [],
                                        "localizedPlaceholder": None,
                                        "addressRenderOptions": None,
                                        "localizedYearPlaceholder": "",
                                        "localizedMonthPlaceholder": "",
                                        "localizedDayPlaceholder": ""
                                    },
                                    "usage": [
                                        "USAGE_APPLE_WALLET",
                                        "USAGE_GOOGLE_PAY"
                                    ],
                                    "googlePayFieldRenderOptions": {
                                        "googlePayPosition": "GOOGLE_PAY_LOYALTY_REWARDS_TIER",
                                        "textModulePriority": 0
                                    },
                                    "defaultTelCountryCode": ""
                                },
                                {
                                    "uniqueName": "person.emailAddress",
                                    "templateId": "",
                                    "fieldType": "PII",
                                    "label": "Email",
                                    "localizedLabel": None,
                                    "dataType": "EMAIL",
                                    "defaultValue": "",
                                    "localizedDefaultValue": None,
                                    "validation": "",
                                    "currencyCode": "",
                                    "appleWalletFieldRenderOptions": {
                                        "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                        "positionSettings": {
                                            "section": "FIELD_SECTION_DO_NOT_USE",
                                            "priority": 0
                                        },
                                        "changeMessage": "",
                                        "localizedChangeMessage": None,
                                        "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                        "suppressLinkDetection": [],
                                    },
                                    "dataCollectionFieldRenderOptions": {
                                        "helpText": "",
                                        "localizedHelpText": None,
                                        "displayOrder": 0,
                                        "placeholder": "",
                                        "selectOptions": [],
                                        "localizedPlaceholder": None,
                                        "addressRenderOptions": None,
                                        "localizedYearPlaceholder": "",
                                        "localizedMonthPlaceholder": "",
                                        "localizedDayPlaceholder": ""
                                    },
                                    "usage": [
                                        "USAGE_DATA_COLLECTION_PAGE"
                                    ],
                                    "googlePayFieldRenderOptions": {
                                        "googlePayPosition": "GOOGLE_PAY_FIELD_DO_NOT_USE",
                                        "textModulePriority": 0
                                    },
                                    "defaultTelCountryCode": ""
                                },
                                {
                                    "uniqueName": "universal.info",
                                    "templateId": "",
                                    "fieldType": "UNIVERSAL_FIELDS",
                                    "label": "Information",
                                    "localizedLabel": None,
                                    "dataType": "TEXT_LONG",
                                    "defaultValue": "Tell your members about their exclusive benefits here.",
                                    "localizedDefaultValue": None,
                                    "validation": "",
                                    "currencyCode": "",
                                    "appleWalletFieldRenderOptions": {
                                        "textAlignment": "LEFT",
                                        "positionSettings": {
                                            "section": "BACK_FIELDS",
                                            "priority": 0
                                        },
                                        "changeMessage": "",
                                        "localizedChangeMessage": None,
                                        "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                        "suppressLinkDetection": [],
                                    },
                                    "dataCollectionFieldRenderOptions": {
                                        "helpText": "",
                                        "localizedHelpText": None,
                                        "displayOrder": 0,
                                        "placeholder": "",
                                        "selectOptions": [],
                                        "localizedPlaceholder": None,
                                        "addressRenderOptions": None,
                                        "localizedYearPlaceholder": "",
                                        "localizedMonthPlaceholder": "",
                                        "localizedDayPlaceholder": ""
                                    },
                                    "usage": [
                                        "USAGE_APPLE_WALLET",
                                        "USAGE_GOOGLE_PAY"
                                    ],
                                    "googlePayFieldRenderOptions": {
                                        "googlePayPosition": "GOOGLE_PAY_TEXT_MODULE",
                                        "textModulePriority": 1
                                    },
                                    "defaultTelCountryCode": ""
                                },
                                {
                                    "uniqueName": "custom.right",
                                    "templateId": "",
                                    "fieldType": "CUSTOM_FIELDS",
                                    "label": f"{kwargs['right_header']}",
                                    "localizedLabel": None,
                                    "dataType": "TEXT",
                                    "defaultValue": f"{kwargs['right_body']}",
                                    "localizedDefaultValue": None,
                                    "validation": "",
                                    "currencyCode": "",
                                    "appleWalletFieldRenderOptions": {
                                        "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                        "positionSettings": {
                                            "section": "FIELD_SECTION_DO_NOT_USE",
                                            "priority": 0
                                        },
                                        "changeMessage": "",
                                        "localizedChangeMessage": None,
                                        "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                        "suppressLinkDetection": [],
                                    },
                                    "dataCollectionFieldRenderOptions": {
                                        "helpText": "",
                                        "localizedHelpText": None,
                                        "displayOrder": 0,
                                        "placeholder": "",
                                        "selectOptions": [],
                                        "localizedPlaceholder": None,
                                        "addressRenderOptions": None,
                                        "localizedYearPlaceholder": "",
                                        "localizedMonthPlaceholder": "",
                                        "localizedDayPlaceholder": ""
                                    },
                                    "usage": [
                                        "USAGE_GOOGLE_PAY"
                                    ],
                                    "googlePayFieldRenderOptions": {
                                        "googlePayPosition": "GOOGLE_PAY_LOYALTY_SECONDARY_POINTS",
                                        "textModulePriority": 0
                                    },
                                    "defaultTelCountryCode": ""
                                },
                                {
                                    "uniqueName": "custom.left",
                                    "templateId": "",
                                    "fieldType": "CUSTOM_FIELDS",
                                    "label": f"{kwargs['left_header']}",
                                    "localizedLabel": None,
                                    "dataType": "TEXT",
                                    "defaultValue": f"{kwargs['left_body']}",
                                    "localizedDefaultValue": None,
                                    "validation": "",
                                    "currencyCode": "",
                                    "appleWalletFieldRenderOptions": {
                                        "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                        "positionSettings": {
                                            "section": "FIELD_SECTION_DO_NOT_USE",
                                            "priority": 0
                                        },
                                        "changeMessage": "",
                                        "localizedChangeMessage": None,
                                        "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                        "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                        "suppressLinkDetection": [],
                                    },
                                    "dataCollectionFieldRenderOptions": {
                                        "helpText": "",
                                        "localizedHelpText": None,
                                        "displayOrder": 0,
                                        "placeholder": "",
                                        "selectOptions": [],
                                        "localizedPlaceholder": None,
                                        "addressRenderOptions": None,
                                        "localizedYearPlaceholder": "",
                                        "localizedMonthPlaceholder": "",
                                        "localizedDayPlaceholder": ""
                                    },
                                    "usage": [
                                        "USAGE_GOOGLE_PAY"
                                    ],
                                    "googlePayFieldRenderOptions": {
                                        "googlePayPosition": "GOOGLE_PAY_LOYALTY_POINTS",
                                        "textModulePriority": 0
                                    },
                                    "defaultTelCountryCode": ""
                                }
                            ],
                            "dataCollectionPageSettings": {
                                "title": "Enrol Below",
                                "localizedTitle": None,
                                "description": "",
                                "localizedDescription": None,
                                "submitButtonText": "Enrol",
                                "localizedSubmitButtonText": None,
                                "loadingText": "Hang on",
                                "localizedLoadingText": None,
                                "thankYouText": "Thank you for enrolling, we will redirect you to your pass.",
                                "localizedThankYouText": None,
                                "pageBackgroundColor": "",
                                "localizedPageBackgroundColor": None,
                                "trackingSettings": None,
                                "submitButtonTextColor": "",
                                "submitButtonBackgroundColor": "",
                                "footerText": "",
                                "localizedFooterText": None,
                                "cssOverrides": "",
                                "passwordSettings": None
                            }
                        },
                        "imageIds": {
                            "icon": f"{img['icon']}",
                            "logo": f"{img['logo']}",
                            "appleLogo": f"{img['appleLogo']}",
                            "hero": f"{img['hero']}",
                            "eventStrip": "",
                            "strip": f"{img['strip']}",
                            "thumbnail": "",
                            "background": "",
                            "footer": "",
                            "security": "",
                            "privilege": "",
                            "airlineAlliance": "",
                            "personalization": "",
                            "banner": "",
                            "message": "",
                            "profile": "",
                            "appImage": "",
                            "stampedImage": "",
                            "unstampedImage": "",
                            "stampImage": ""
                        },
                        "colors": {
                            "backgroundColor": f"#{kwargs['color_background']}",
                            "labelColor": f"#{kwargs['color_title']}",
                            "textColor": f"#{kwargs['color_text']}",
                            "stripColor": ""
                        },
                        "barcode": {
                            "payload": " ${pid}",
                            "format": "PDF417",
                            "altText": "${pid}",
                            "localizedAltText": None,
                            "messageEncoding": "utf8",
                            "totpParameters": None
                        },
                        "nfcEnabled": {
                            "certificateId": "",
                            "payload": ""
                        },
                        "sharing": {
                            "url": "",
                            "description": "",
                            "localizedDescription": None
                        },
                        "appleWalletSettings": {
                            "passType": "STORE_CARD",
                            "userInfo": "",
                            "appLaunchUrl": "",
                            "associatedStoreIdentifiers": [],
                            "maxDistance": 0,
                            "appStoreCountries": [],
                            "transitType": "TRANSIT_TYPE_DO_NOT_USE",
                            "groupingIdentifier": "",
                            "personalizationDetails": None,
                            "appStoreIdentifiers": []
                        },
                        "googlePaySettings": {
                            "passType": "LOYALTY",
                            "androidApp": None,
                            "iosApp": None,
                            "webApp": None,
                            "backgroundColor": "",
                            "languageOverrides": []
                        },
                        "locations": [],
                        "beacons": [],
                        "links": [],
                        "timezone": "Europe/Moscow",
                        "expirySettings": {
                            "expiryType": "EXPIRE_NONE"
                        },
                        "landingPageSettings": {
                            "landingLocalizationOverride": [],
                            "preferThirdPartyAndroidWallet": "OFF",
                            "preferredAndroidWallet": "ANDROID_WALLET_WALLETPASSES",
                            "localizedTextOverrides": {}
                        },
                    }
                    template = await session.post(url=self.api_url + "template", json=body, headers=header)
                    template_id = (await template.json())['id']
                    body_par = {
                        'id': 'blue',
                        'tierIndex': 1,
                        'name': f'{kwargs["corp_name"]}',
                        'programId': app_id,
                        'passTemplateId': template_id,
                        'timezone': 'Europe/Moscow'
                    }

                    async with session.post(url=self.api_url + "members/tier", json=body_par,
                                            headers=header) as tier:
                        print(await tier.text())
                        return {'tierId': template_id, 'programId': app_id}
        except Exception as error:
            print("Error creating the application ", error)

    async def create_member(self, program_id):
        header = await self.auth()
        async with aiohttp.ClientSession() as session:
            req = await session.get(url=self.api_url + f'members/enrol/url/program/{program_id}', headers=header)
            print(await req.json())
            return await req.json()

    async def update_card(self, **kwargs):
        header = await self.auth()

        async with aiohttp.ClientSession() as session:
            img = await self.upload_image(kwargs['logo'], kwargs['background'], kwargs['icon_push'])

            if kwargs['barcode'] == 'Отсутсвует':
                body_update = {
                    "id": kwargs['template_id'],
                    "name": kwargs['corp_name'],
                    "protocol": "MEMBERSHIP",
                    "revision": 1,
                    "defaultLanguage": "RU",
                    "organizationName": f"{kwargs['corp_name']}",
                    "localizedOrganizationName": None,
                    "description": "Your special card",
                    "localizedDescription": None,
                    "data": {
                        "dataFields": [
                            {
                                'uniqueName': 'custom.topText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["top_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["top_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'HEADER_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.leftText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["left_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["left_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.rightText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["right_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["right_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'RIGHT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 1
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                "uniqueName": "custom.left",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['left_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['left_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                            {
                                "uniqueName": "custom.right",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['right_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['right_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_SECONDARY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                        ],
                        "dataCollectionPageSettings": {
                            "title": "Enrol Below",
                            "localizedTitle": None,
                            "description": "",
                            "localizedDescription": None,
                            "submitButtonText": "Enrol",
                            "localizedSubmitButtonText": None,
                            "loadingText": "Hang on",
                            "localizedLoadingText": None,
                            "thankYouText": "Thank you for enrolling, we will redirect you to your pass.",
                            "localizedThankYouText": None,
                            "pageBackgroundColor": "",
                            "localizedPageBackgroundColor": None,
                            "trackingSettings": None,
                            "submitButtonTextColor": "",
                            "submitButtonBackgroundColor": "",
                            "footerText": "",
                            "localizedFooterText": None,
                            "cssOverrides": "",
                            "passwordSettings": None
                        }
                    },
                    "imageIds": {
                        "icon": f"{img['icon']}",
                        "logo": f"{img['logo']}",
                        "appleLogo": f"{img['appleLogo']}",
                        "hero": f"{img['hero']}",
                        "eventStrip": "",
                        "strip": f"{img['strip']}",
                        "thumbnail": "",
                        "background": "",
                        "footer": "",
                        "security": "",
                        "privilege": "",
                        "airlineAlliance": "",
                        "personalization": "",
                        "banner": "",
                        "message": "",
                        "profile": "",
                        "appImage": "",
                        "stampedImage": "",
                        "unstampedImage": "",
                        "stampImage": ""
                    },
                    "colors": {
                        "backgroundColor": f"#{kwargs['color_background']}",
                        "labelColor": f"#{kwargs['color_title']}",
                        "textColor": f"#{kwargs['color_text']}",
                        "stripColor": ""
                    },
                    "barcode": {
                        "payload": " ${pid}",
                        "format": "PDF417",
                        "altText": "${pid}",
                        "localizedAltText": None,
                        "messageEncoding": "utf8",
                        "totpParameters": None
                    },
                    "nfcEnabled": {
                        "certificateId": "",
                        "payload": ""
                    },
                    "sharing": {
                        "url": "",
                        "description": "",
                        "localizedDescription": None
                    },
                    "appleWalletSettings": {
                        "passType": "STORE_CARD",
                        "userInfo": "",
                        "appLaunchUrl": "",
                        "associatedStoreIdentifiers": [],
                        "maxDistance": 0,
                        "appStoreCountries": [],
                        "transitType": "TRANSIT_TYPE_DO_NOT_USE",
                        "groupingIdentifier": "",
                        "personalizationDetails": None,
                        "appStoreIdentifiers": []
                    },
                    "googlePaySettings": {
                        "passType": "LOYALTY",
                        "androidApp": None,
                        "iosApp": None,
                        "webApp": None,
                        "backgroundColor": "",
                        "languageOverrides": []
                    },
                    "locations": [],
                    "beacons": [],
                    "links": [],
                    "timezone": "Europe/Moscow",
                    "expirySettings": {
                        "expiryType": "EXPIRE_NONE"
                    },
                    "landingPageSettings": {
                        "landingLocalizationOverride": [],
                        "preferThirdPartyAndroidWallet": "OFF",
                        "preferredAndroidWallet": "ANDROID_WALLET_WALLETPASSES",
                        "localizedTextOverrides": {}
                    },
                }
            elif kwargs['barcode'] == 'qr':
                print('ДАД АДУДАДУКДАУКДПШОЩУКПЩУКПЩШ')
                body_update = {
                    "id": kwargs['template_id'],
                    "name": kwargs['corp_name'],
                    "protocol": "MEMBERSHIP",
                    "revision": 1,
                    "defaultLanguage": "RU",
                    "organizationName": f"{kwargs['corp_name']}",
                    "localizedOrganizationName": None,
                    "description": "Your special card",
                    "localizedDescription": None,
                    "data": {
                        "dataFields": [
                            {
                                'uniqueName': 'custom.topText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["top_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["top_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'HEADER_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.leftText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["left_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["left_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.rightText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["right_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["right_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'RIGHT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 1
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                "uniqueName": "custom.left",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['left_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['left_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                            {
                                "uniqueName": "custom.right",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['right_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['right_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_SECONDARY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                        ],
                        "dataCollectionPageSettings": {
                            "title": "Enrol Below",
                            "localizedTitle": None,
                            "description": "",
                            "localizedDescription": None,
                            "submitButtonText": "Enrol",
                            "localizedSubmitButtonText": None,
                            "loadingText": "Hang on",
                            "localizedLoadingText": None,
                            "thankYouText": "Thank you for enrolling, we will redirect you to your pass.",
                            "localizedThankYouText": None,
                            "pageBackgroundColor": "",
                            "localizedPageBackgroundColor": None,
                            "trackingSettings": None,
                            "submitButtonTextColor": "",
                            "submitButtonBackgroundColor": "",
                            "footerText": "",
                            "localizedFooterText": None,
                            "cssOverrides": "",
                            "passwordSettings": None
                        }
                    },
                    "imageIds": {
                        "icon": f"{img['icon']}",
                        "logo": f"{img['logo']}",
                        "appleLogo": f"{img['appleLogo']}",
                        "hero": f"{img['hero']}",
                        "eventStrip": "",
                        "strip": f"{img['strip']}",
                        "thumbnail": "",
                        "background": "",
                        "footer": "",
                        "security": "",
                        "privilege": "",
                        "airlineAlliance": "",
                        "personalization": "",
                        "banner": "",
                        "message": "",
                        "profile": "",
                        "appImage": "",
                        "stampedImage": "",
                        "unstampedImage": "",
                        "stampImage": ""
                    },
                    "colors": {
                        "backgroundColor": f"#{kwargs['color_background']}",
                        "labelColor": f"#{kwargs['color_title']}",
                        "textColor": f"#{kwargs['color_text']}",
                        "stripColor": ""
                    },
                    "barcode": {
                        "payload": " ${pid}",
                        "format": "QR",
                        "altText": "${pid}",
                        "localizedAltText": None,
                        "messageEncoding": "utf8",
                        "totpParameters": None
                    },
                    "nfcEnabled": {
                        "certificateId": "",
                        "payload": ""
                    },
                    "sharing": {
                        "url": "",
                        "description": "",
                        "localizedDescription": None
                    },
                    "appleWalletSettings": {
                        "passType": "STORE_CARD",
                        "userInfo": "",
                        "appLaunchUrl": "",
                        "associatedStoreIdentifiers": [],
                        "maxDistance": 0,
                        "appStoreCountries": [],
                        "transitType": "TRANSIT_TYPE_DO_NOT_USE",
                        "groupingIdentifier": "",
                        "personalizationDetails": None,
                        "appStoreIdentifiers": []
                    },
                    "googlePaySettings": {
                        "passType": "LOYALTY",
                        "androidApp": None,
                        "iosApp": None,
                        "webApp": None,
                        "backgroundColor": "",
                        "languageOverrides": []
                    },
                    "locations": [],
                    "beacons": [],
                    "links": [],
                    "timezone": "Europe/Moscow",
                    "expirySettings": {
                        "expiryType": "EXPIRE_NONE"
                    },
                    "landingPageSettings": {
                        "landingLocalizationOverride": [],
                        "preferThirdPartyAndroidWallet": "OFF",
                        "preferredAndroidWallet": "ANDROID_WALLET_WALLETPASSES",
                        "localizedTextOverrides": {}
                    },
                }
            else:
                body_update = {
                    "id": kwargs['template_id'],
                    "name": kwargs['corp_name'],
                    "protocol": "MEMBERSHIP",
                    "revision": 1,
                    "defaultLanguage": "RU",
                    "organizationName": f"{kwargs['corp_name']}",
                    "localizedOrganizationName": None,
                    "description": "Your special card",
                    "localizedDescription": None,
                    "data": {
                        "dataFields": [
                            {
                                'uniqueName': 'custom.topText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["top_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["top_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'HEADER_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.leftText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["left_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["left_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.rightText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["right_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["right_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'RIGHT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 1
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                "uniqueName": "custom.left",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['left_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['left_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                            {
                                "uniqueName": "custom.right",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['right_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['right_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_SECONDARY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                        ],
                        "dataCollectionPageSettings": {
                            "title": "Enrol Below",
                            "localizedTitle": None,
                            "description": "",
                            "localizedDescription": None,
                            "submitButtonText": "Enrol",
                            "localizedSubmitButtonText": None,
                            "loadingText": "Hang on",
                            "localizedLoadingText": None,
                            "thankYouText": "Thank you for enrolling, we will redirect you to your pass.",
                            "localizedThankYouText": None,
                            "pageBackgroundColor": "",
                            "localizedPageBackgroundColor": None,
                            "trackingSettings": None,
                            "submitButtonTextColor": "",
                            "submitButtonBackgroundColor": "",
                            "footerText": "",
                            "localizedFooterText": None,
                            "cssOverrides": "",
                            "passwordSettings": None
                        }
                    },
                    "imageIds": {
                        "icon": f"{img['icon']}",
                        "logo": f"{img['logo']}",
                        "appleLogo": f"{img['appleLogo']}",
                        "hero": f"{img['hero']}",
                        "eventStrip": "",
                        "strip": f"{img['strip']}",
                        "thumbnail": "",
                        "background": "",
                        "footer": "",
                        "security": "",
                        "privilege": "",
                        "airlineAlliance": "",
                        "personalization": "",
                        "banner": "",
                        "message": "",
                        "profile": "",
                        "appImage": "",
                        "stampedImage": "",
                        "unstampedImage": "",
                        "stampImage": ""
                    },
                    "colors": {
                        "backgroundColor": f"#{kwargs['color_background']}",
                        "labelColor": f"#{kwargs['color_title']}",
                        "textColor": f"#{kwargs['color_text']}",
                        "stripColor": ""
                    },
                    "barcode": {
                        "payload": " ${pid}",
                        "format": "PDF417",
                        "altText": "${pid}",
                        "localizedAltText": None,
                        "messageEncoding": "utf8",
                        "totpParameters": None
                    },
                    "nfcEnabled": {
                        "certificateId": "",
                        "payload": ""
                    },
                    "sharing": {
                        "url": "",
                        "description": "",
                        "localizedDescription": None
                    },
                    "appleWalletSettings": {
                        "passType": "STORE_CARD",
                        "userInfo": "",
                        "appLaunchUrl": "",
                        "associatedStoreIdentifiers": [],
                        "maxDistance": 0,
                        "appStoreCountries": [],
                        "transitType": "TRANSIT_TYPE_DO_NOT_USE",
                        "groupingIdentifier": "",
                        "personalizationDetails": None,
                        "appStoreIdentifiers": []
                    },
                    "googlePaySettings": {
                        "passType": "LOYALTY",
                        "androidApp": None,
                        "iosApp": None,
                        "webApp": None,
                        "backgroundColor": "",
                        "languageOverrides": []
                    },
                    "locations": [],
                    "beacons": [],
                    "links": [],
                    "timezone": "Europe/Moscow",
                    "expirySettings": {
                        "expiryType": "EXPIRE_NONE"
                    },
                    "landingPageSettings": {
                        "landingLocalizationOverride": [],
                        "preferThirdPartyAndroidWallet": "OFF",
                        "preferredAndroidWallet": "ANDROID_WALLET_WALLETPASSES",
                        "localizedTextOverrides": {}
                    },
                }
            try:
                template = await session.put(url=self.api_url + "template", json=body_update, headers=header)
                print(await template.json())
            except Exception as error:
                print(error)

    async def create_push(self, **kwargs):
        header = await self.auth()

        async with aiohttp.ClientSession() as session:
            id_push = await session.post(
                url=self.api_url + "location",
                json={"name": "test", "lat": f"{kwargs['lat']}", "lon": f"{kwargs['lon']}", "alt": 0,
                      "lockScreenMessage": f"{kwargs['description']}", "localizedLockScreenMessage": None,
                      "position": 0},
                headers=header
            )
            push_id = await id_push.json()
            img = await self.upload_image(kwargs['logo'], kwargs['background'], kwargs['icon_push'])
            if kwargs['barcode'] == 'Отсутсвует':
                body_update = {
                    "id": kwargs['template_id'],
                    "name": kwargs['corp_name'],
                    "protocol": "MEMBERSHIP",
                    "revision": 1,
                    "defaultLanguage": "RU",
                    "organizationName": f"{kwargs['corp_name']}",
                    "localizedOrganizationName": None,
                    "description": "Your special card",
                    "localizedDescription": None,
                    "data": {
                        "dataFields": [
                            {
                                'uniqueName': 'custom.topText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["top_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["top_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'HEADER_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.leftText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["left_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["left_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.rightText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["right_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["right_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'RIGHT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 1
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                "uniqueName": "custom.left",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['left_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['left_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                            {
                                "uniqueName": "custom.right",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['right_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['right_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_SECONDARY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                        ],
                        "dataCollectionPageSettings": {
                            "title": "Enrol Below",
                            "localizedTitle": None,
                            "description": "",
                            "localizedDescription": None,
                            "submitButtonText": "Enrol",
                            "localizedSubmitButtonText": None,
                            "loadingText": "Hang on",
                            "localizedLoadingText": None,
                            "thankYouText": "Thank you for enrolling, we will redirect you to your pass.",
                            "localizedThankYouText": None,
                            "pageBackgroundColor": "",
                            "localizedPageBackgroundColor": None,
                            "trackingSettings": None,
                            "submitButtonTextColor": "",
                            "submitButtonBackgroundColor": "",
                            "footerText": "",
                            "localizedFooterText": None,
                            "cssOverrides": "",
                            "passwordSettings": None
                        }
                    },
                    "imageIds": {
                        "icon": f"{img['icon']}",
                        "logo": f"{img['logo']}",
                        "appleLogo": f"{img['appleLogo']}",
                        "hero": f"{img['hero']}",
                        "eventStrip": "",
                        "strip": f"{img['strip']}",
                        "thumbnail": "",
                        "background": "",
                        "footer": "",
                        "security": "",
                        "privilege": "",
                        "airlineAlliance": "",
                        "personalization": "",
                        "banner": "",
                        "message": "",
                        "profile": "",
                        "appImage": "",
                        "stampedImage": "",
                        "unstampedImage": "",
                        "stampImage": ""
                    },
                    "colors": {
                        "backgroundColor": f"#{kwargs['color_background']}",
                        "labelColor": f"#{kwargs['color_title']}",
                        "textColor": f"#{kwargs['color_text']}",
                        "stripColor": ""
                    },
                    "barcode": {
                        "payload": " ${pid}",
                        "format": "PDF417",
                        "altText": "${pid}",
                        "localizedAltText": None,
                        "messageEncoding": "utf8",
                        "totpParameters": None
                    },
                    "nfcEnabled": {
                        "certificateId": "",
                        "payload": ""
                    },
                    "sharing": {
                        "url": "",
                        "description": "",
                        "localizedDescription": None
                    },
                    "appleWalletSettings": {
                        "passType": "STORE_CARD",
                        "userInfo": "",
                        "appLaunchUrl": "",
                        "associatedStoreIdentifiers": [],
                        "maxDistance": 0,
                        "appStoreCountries": [],
                        "transitType": "TRANSIT_TYPE_DO_NOT_USE",
                        "groupingIdentifier": "",
                        "personalizationDetails": None,
                        "appStoreIdentifiers": []
                    },
                    "googlePaySettings": {
                        "passType": "LOYALTY",
                        "androidApp": None,
                        "iosApp": None,
                        "webApp": None,
                        "backgroundColor": "",
                        "languageOverrides": []
                    },
                    "locations": [
                        {
                            "id": f"{push_id['id']}",
                            "name": "test",
                            "lat": f"{kwargs['lat']}",
                            "lon": f"{kwargs['lon']}",
                            "alt": 0,
                            "lockScreenMessage": f"{kwargs['description']}",
                            "localizedLockScreenMessage": None,
                            "position": 0
                        }
                    ],
                    "beacons": [],
                    "links": [],
                    "timezone": "Europe/Moscow",
                    "expirySettings": {
                        "expiryType": "EXPIRE_NONE"
                    },
                    "landingPageSettings": {
                        "landingLocalizationOverride": [],
                        "preferThirdPartyAndroidWallet": "OFF",
                        "preferredAndroidWallet": "ANDROID_WALLET_WALLETPASSES",
                        "localizedTextOverrides": {}
                    },
                }
            elif kwargs['barcode'] == 'qr':
                body_update = {
                    "id": kwargs['template_id'],
                    "name": kwargs['corp_name'],
                    "protocol": "MEMBERSHIP",
                    "revision": 1,
                    "defaultLanguage": "RU",
                    "organizationName": f"{kwargs['corp_name']}",
                    "localizedOrganizationName": None,
                    "description": "Your special card",
                    "localizedDescription": None,
                    "data": {
                        "dataFields": [
                            {
                                'uniqueName': 'custom.topText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["top_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["top_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'HEADER_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.leftText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["left_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["left_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.rightText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["right_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["right_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'RIGHT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 1
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                "uniqueName": "custom.left",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['left_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['left_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                            {
                                "uniqueName": "custom.right",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['right_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['right_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_SECONDARY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                        ],
                        "dataCollectionPageSettings": {
                            "title": "Enrol Below",
                            "localizedTitle": None,
                            "description": "",
                            "localizedDescription": None,
                            "submitButtonText": "Enrol",
                            "localizedSubmitButtonText": None,
                            "loadingText": "Hang on",
                            "localizedLoadingText": None,
                            "thankYouText": "Thank you for enrolling, we will redirect you to your pass.",
                            "localizedThankYouText": None,
                            "pageBackgroundColor": "",
                            "localizedPageBackgroundColor": None,
                            "trackingSettings": None,
                            "submitButtonTextColor": "",
                            "submitButtonBackgroundColor": "",
                            "footerText": "",
                            "localizedFooterText": None,
                            "cssOverrides": "",
                            "passwordSettings": None
                        }
                    },
                    "imageIds": {
                        "icon": f"{img['icon']}",
                        "logo": f"{img['logo']}",
                        "appleLogo": f"{img['appleLogo']}",
                        "hero": f"{img['hero']}",
                        "eventStrip": "",
                        "strip": f"{img['strip']}",
                        "thumbnail": "",
                        "background": "",
                        "footer": "",
                        "security": "",
                        "privilege": "",
                        "airlineAlliance": "",
                        "personalization": "",
                        "banner": "",
                        "message": "",
                        "profile": "",
                        "appImage": "",
                        "stampedImage": "",
                        "unstampedImage": "",
                        "stampImage": ""
                    },
                    "colors": {
                        "backgroundColor": f"#{kwargs['color_background']}",
                        "labelColor": f"#{kwargs['color_title']}",
                        "textColor": f"#{kwargs['color_text']}",
                        "stripColor": ""
                    },
                    "barcode": {
                        "payload": " ${pid}",
                        "format": "QR",
                        "altText": "${pid}",
                        "localizedAltText": None,
                        "messageEncoding": "utf8",
                        "totpParameters": None
                    },
                    "nfcEnabled": {
                        "certificateId": "",
                        "payload": ""
                    },
                    "sharing": {
                        "url": "",
                        "description": "",
                        "localizedDescription": None
                    },
                    "appleWalletSettings": {
                        "passType": "STORE_CARD",
                        "userInfo": "",
                        "appLaunchUrl": "",
                        "associatedStoreIdentifiers": [],
                        "maxDistance": 0,
                        "appStoreCountries": [],
                        "transitType": "TRANSIT_TYPE_DO_NOT_USE",
                        "groupingIdentifier": "",
                        "personalizationDetails": None,
                        "appStoreIdentifiers": []
                    },
                    "googlePaySettings": {
                        "passType": "LOYALTY",
                        "androidApp": None,
                        "iosApp": None,
                        "webApp": None,
                        "backgroundColor": "",
                        "languageOverrides": []
                    },
                    "locations": [
                        {
                            "id": f"{push_id['id']}",
                            "name": "test",
                            "lat": f"{kwargs['lat']}",
                            "lon": f"{kwargs['lon']}",
                            "alt": 0,
                            "lockScreenMessage": f"{kwargs['description']}",
                            "localizedLockScreenMessage": None,
                            "position": 0
                        }
                    ],
                    "beacons": [],
                    "links": [],
                    "timezone": "Europe/Moscow",
                    "expirySettings": {
                        "expiryType": "EXPIRE_NONE"
                    },
                    "landingPageSettings": {
                        "landingLocalizationOverride": [],
                        "preferThirdPartyAndroidWallet": "OFF",
                        "preferredAndroidWallet": "ANDROID_WALLET_WALLETPASSES",
                        "localizedTextOverrides": {}
                    },
                }
            else:
                body_update = {
                    "id": kwargs['template_id'],
                    "name": kwargs['corp_name'],
                    "protocol": "MEMBERSHIP",
                    "revision": 1,
                    "defaultLanguage": "RU",
                    "organizationName": f"{kwargs['corp_name']}",
                    "localizedOrganizationName": None,
                    "description": "Your special card",
                    "localizedDescription": None,
                    "data": {
                        "dataFields": [
                            {
                                'uniqueName': 'custom.topText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["top_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["top_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'HEADER_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.leftText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["left_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["left_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'LEFT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 0
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                'uniqueName': 'custom.rightText',
                                'templateId': '',
                                'fieldType': 'CUSTOM_FIELDS',
                                'isRequired': False,
                                'label': f'{kwargs["right_header"]}',
                                'localizedLabel': None,
                                'dataType': 'TEXT',
                                'defaultValue': f'{kwargs["right_body"]}',
                                'localizedDefaultValue': None,
                                'validation': '',
                                'userCanSetValue': True,
                                'currencyCode': '',
                                'appleWalletFieldRenderOptions': {
                                    'textAlignment': 'RIGHT',
                                    'positionSettings': {
                                        'section': 'SECONDARY_FIELDS',
                                        'priority': 1
                                    },
                                    'changeMessage': '',
                                    'localizedChangeMessage': None,
                                    'dateStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'timeStyle': 'DATE_TIME_STYLE_DO_NOT_USE',
                                    'numberStyle': 'NUMBER_STYLE_DO_NOT_USE',
                                    'suppressLinkDetection': [],
                                    'ignoreTimezone': False,
                                    'isRelativeDate': False
                                },
                                'dataCollectionFieldRenderOptions': {
                                    'helpText': '',
                                    'localizedHelpText': None,
                                    'displayOrder': 0,
                                    'placeholder': '',
                                    'selectOptions': [],
                                    'localizedPlaceholder': None,
                                    'autocomplete': False,
                                    'addressRenderOptions': None,
                                    'localizedYearPlaceholder': '',
                                    'localizedMonthPlaceholder': '',
                                    'localizedDayPlaceholder': ''
                                },
                                'usage': ['USAGE_APPLE_WALLET'],
                                'googlePayFieldRenderOptions': {
                                    'googlePayPosition': 'GOOGLE_PAY_FIELD_DO_NOT_USE',
                                    'textModulePriority': 0
                                },
                                'defaultTelCountryCode': ''
                            },
                            {
                                "uniqueName": "custom.left",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['left_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['left_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                            {
                                "uniqueName": "custom.right",
                                "templateId": "",
                                "fieldType": "CUSTOM_FIELDS",
                                "label": f"{kwargs['right_header']}",
                                "localizedLabel": None,
                                "dataType": "TEXT",
                                "defaultValue": f"{kwargs['right_body']}",
                                "localizedDefaultValue": None,
                                "validation": "",
                                "currencyCode": "",
                                "appleWalletFieldRenderOptions": {
                                    "textAlignment": "TEXT_ALIGNMENT_DO_NOT_USE",
                                    "positionSettings": {
                                        "section": "FIELD_SECTION_DO_NOT_USE",
                                        "priority": 0
                                    },
                                    "changeMessage": "",
                                    "localizedChangeMessage": None,
                                    "dateStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "timeStyle": "DATE_TIME_STYLE_DO_NOT_USE",
                                    "numberStyle": "NUMBER_STYLE_DO_NOT_USE",
                                    "suppressLinkDetection": [],
                                },
                                "dataCollectionFieldRenderOptions": {
                                    "helpText": "",
                                    "localizedHelpText": None,
                                    "displayOrder": 0,
                                    "placeholder": "",
                                    "selectOptions": [],
                                    "localizedPlaceholder": None,
                                    "addressRenderOptions": None,
                                    "localizedYearPlaceholder": "",
                                    "localizedMonthPlaceholder": "",
                                    "localizedDayPlaceholder": ""
                                },
                                "usage": [
                                    "USAGE_GOOGLE_PAY"
                                ],
                                "googlePayFieldRenderOptions": {
                                    "googlePayPosition": "GOOGLE_PAY_LOYALTY_SECONDARY_POINTS",
                                    "textModulePriority": 0
                                },
                                "defaultTelCountryCode": ""
                            },
                        ],
                        "dataCollectionPageSettings": {
                            "title": "Enrol Below",
                            "localizedTitle": None,
                            "description": "",
                            "localizedDescription": None,
                            "submitButtonText": "Enrol",
                            "localizedSubmitButtonText": None,
                            "loadingText": "Hang on",
                            "localizedLoadingText": None,
                            "thankYouText": "Thank you for enrolling, we will redirect you to your pass.",
                            "localizedThankYouText": None,
                            "pageBackgroundColor": "",
                            "localizedPageBackgroundColor": None,
                            "trackingSettings": None,
                            "submitButtonTextColor": "",
                            "submitButtonBackgroundColor": "",
                            "footerText": "",
                            "localizedFooterText": None,
                            "cssOverrides": "",
                            "passwordSettings": None
                        }
                    },
                    "imageIds": {
                        "icon": f"{img['icon']}",
                        "logo": f"{img['logo']}",
                        "appleLogo": f"{img['appleLogo']}",
                        "hero": f"{img['hero']}",
                        "eventStrip": "",
                        "strip": f"{img['strip']}",
                        "thumbnail": "",
                        "background": "",
                        "footer": "",
                        "security": "",
                        "privilege": "",
                        "airlineAlliance": "",
                        "personalization": "",
                        "banner": "",
                        "message": "",
                        "profile": "",
                        "appImage": "",
                        "stampedImage": "",
                        "unstampedImage": "",
                        "stampImage": ""
                    },
                    "colors": {
                        "backgroundColor": f"#{kwargs['color_background']}",
                        "labelColor": f"#{kwargs['color_title']}",
                        "textColor": f"#{kwargs['color_text']}",
                        "stripColor": ""
                    },
                    "barcode": {
                        "payload": " ${pid}",
                        "format": "PDF417",
                        "altText": "${pid}",
                        "localizedAltText": None,
                        "messageEncoding": "utf8",
                        "totpParameters": None
                    },
                    "nfcEnabled": {
                        "certificateId": "",
                        "payload": ""
                    },
                    "sharing": {
                        "url": "",
                        "description": "",
                        "localizedDescription": None
                    },
                    "appleWalletSettings": {
                        "passType": "STORE_CARD",
                        "userInfo": "",
                        "appLaunchUrl": "",
                        "associatedStoreIdentifiers": [],
                        "maxDistance": 0,
                        "appStoreCountries": [],
                        "transitType": "TRANSIT_TYPE_DO_NOT_USE",
                        "groupingIdentifier": "",
                        "personalizationDetails": None,
                        "appStoreIdentifiers": []
                    },
                    "googlePaySettings": {
                        "passType": "LOYALTY",
                        "androidApp": None,
                        "iosApp": None,
                        "webApp": None,
                        "backgroundColor": "",
                        "languageOverrides": []
                    },
                    "locations": [
                        {
                            "id": f"{push_id['id']}",
                            "name": "test",
                            "lat": f"{kwargs['lat']}",
                            "lon": f"{kwargs['lon']}",
                            "alt": 0,
                            "lockScreenMessage": f"{kwargs['description']}",
                            "localizedLockScreenMessage": None,
                            "position": 0
                        }
                    ],
                    "beacons": [],
                    "links": [],
                    "timezone": "Europe/Moscow",
                    "expirySettings": {
                        "expiryType": "EXPIRE_NONE"
                    },
                    "landingPageSettings": {
                        "landingLocalizationOverride": [],
                        "preferThirdPartyAndroidWallet": "OFF",
                        "preferredAndroidWallet": "ANDROID_WALLET_WALLETPASSES",
                        "localizedTextOverrides": {}
                    },
                }
            try:
                template = await session.put(url=self.api_url + "template", json=body_update, headers=header)
                print(await template.json())
            except Exception as error:
                print(error)

    async def test(self):
        header = await self.auth()

        async with aiohttp.ClientSession() as session:
            res = await session.get(
                url=self.api_url + 'template/data/4ny4qTW09sA5YLXMKrU2T9',
                headers=header)
            data = await res.json()
            print(data['template'])
