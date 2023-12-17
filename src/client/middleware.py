# [START imports]
import json
import os
import uuid

from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials
from google.auth import jwt, crypt


# [END imports]

class DemoLoyalty:
    """Demo class for creating and managing Loyalty cards in Google Wallet.

    Attributes:
        key_file_path: Path to service account key file from Google Cloud
            Console. Environment variable: GOOGLE_APPLICATION_CREDENTIALS.
        base_url: Base URL for Google Wallet API requests.
    """

    def __init__(self):
        #current_dir = 'D:/Work/optimist/backend/src/static/keys/digi.json'
        self.key_file_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS',
                                            '/home/luxar/PycharmProjects/optimist/backend/src/static/keys/optimism.json')
                                            #current_dir)
        self.base_url = 'https://walletobjects.googleapis.com/walletobjects/v1'
        self.batch_url = 'https://walletobjects.googleapis.com/batch'
        self.class_url = f'{self.base_url}/loyaltyClass'
        self.object_url = f'{self.base_url}/loyaltyObject'

        # Set up authenticated client
        self.auth()

    # [END setup]

    # [START auth]
    def auth(self):
        """Create authenticated HTTP client using a service account file."""
        self.credentials = Credentials.from_service_account_file(
            self.key_file_path,
            scopes=['https://www.googleapis.com/auth/wallet_object.issuer'])

        self.http_client = AuthorizedSession(self.credentials)

    # [END auth]

    # [START createClass]
    def create_class(self,
                     issuer_id: str,
                     class_suffix: str,
                     top_text_content: str,
                     logo: str) -> str:

        # Check if the class exists
        response = self.http_client.get(
            url=f'{self.class_url}/{issuer_id}.{class_suffix}')

        if response.status_code == 200:
            print(f'Class {issuer_id}.{class_suffix} already exists!')
            return f'{issuer_id}.{class_suffix}'
        elif response.status_code != 404:
            # Something else went wrong...
            print(response.text)
            return f'{issuer_id}.{class_suffix}'

        # See link below for more information on required properties
        # https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass
        new_class = {
            'id': f'{issuer_id}.{class_suffix}',
            'issuerName': f'Ряженка',
            'reviewStatus': 'UNDER_REVIEW',
            'programName': f'{top_text_content}',
            'programLogo': {
                'sourceUri': {
                    'uri':
                        'https://i.ibb.co/kx4mbtT/logo.png'
                },
                'contentDescription': {
                    'defaultValue': {
                        'language': 'ru-RU',
                        'value': 'asdasdasdasd'
                    }
                }
            }
        }

        response = self.http_client.post(url=self.class_url, json=new_class)

        print('Class insert response')
        print(response.text)

        return response.json().get('id')

    # [END createClass]

    # [START jwtNew]
    def create_jwt_new_objects(self,
                               issuer_id: str,
                               class_suffix: str,
                               object_suffix: str,
                               top_text_content: str,
                               text_left_header: str,
                               text_left_content,
                               text_right_header: str,
                               text_right_content: str,
                               logo: str,
                               background: str,
                               client_name: str,
                               card_number: str,
                               color: str) -> str:

        # See link below for more information on required properties
        # https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass
        new_class = {
            'id': f'{issuer_id}.{class_suffix}',
            'issuerName': f'Ряженка',
            'reviewStatus': 'UNDER_REVIEW',
            'hexBackgroundColor': f'{color}',
            'programName': f'{top_text_content}',
            'programLogo': {
                'sourceUri': {
                    'uri':
                        f'{logo}'
                },
                'contentDescription': {
                    'defaultValue': {
                        'language': 'ru-RU',
                        'value': '1'
                    }
                }
            }
        }

        # See link below for more information on required properties
        # https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject
        new_object = {
            'id': f'{issuer_id}.{object_suffix}',
            'classId': f'{issuer_id}.{class_suffix}',
            'state': 'ACTIVE',
            'heroImage': {
                'sourceUri': {
                    'uri':
                        f'{background}'
                },
                'contentDescription': {
                    'defaultValue': {
                        'language': 'ru-RU',
                        'value': '2'
                    }
                }
            },
            'barcode': {
                'type': 'QR_CODE',
                'value': 'QR code'
            },
            'hexBackgroundColor': f'{color}',
            'locations': [{
                'latitude': 37.424015499999996,
                'longitude': -122.09259560000001
            }],
            'accountId': f'{card_number}',
            'accountName': f'{client_name}',
            'loyaltyPoints': {
                'label': f'{text_left_header}',
                'balance': {
                    'string': f"{text_left_content}"
                }
            },
            'secondaryLoyaltyPoints': {
                'label': f'{text_right_header}',
                'balance': {
                    'string': f"{text_right_content}"
                }
            },
        }
        # Create the JWT claims
        claims = {
            'iss': self.credentials.service_account_email,
            'aud': 'google',
            'origins': ['www.example.com'],
            'typ': 'savetowallet',
            'payload': {
                # The listed classes and objects will be created
                'loyaltyClasses': [new_class],
                'loyaltyObjects': [new_object]
            },
        }

        # The service account credentials are used to sign the JWT
        signer = crypt.RSASigner.from_service_account_file(self.key_file_path)
        token = jwt.encode(signer, claims).decode('utf-8')

        return f'https://pay.google.com/gp/v/save/{token}'

    # [END jwtNew]

    # [START jwtExisting]
    def create_jwt_existing_objects(self, issuer_id: str) -> str:
        """Сгенерируйте подписанный JWT, который ссылается на существующий объект pass.

         Когда пользователь открывает URL-адрес "Добавить в Google кошелек" и сохраняет пропуск в
        свой кошелек, объекты pass, определенные в JWT, добавляются в
        приложение Google Wallet пользователя. Это позволяет пользователю сохранять несколько
        объектов pass в одном вызове API.

         Добавляемые объекты должны соответствовать приведенному ниже формату:

        {
            'id': 'ISSUER_ID.OBJECT_SUFFIX',
            'classId': 'ISSUER_ID.CLASS_SUFFIX'
        }

        Args:
            issuer_id (str): The issuer ID being used for this request.

        Returns:
            An "Add to Google Wallet" link
        """

        # Multiple pass types can be added at the same time
        # At least one type must be specified in the JWT claims
        # Note: Make sure to replace the placeholder class and object suffixes
        objects_to_add = {
            # Event tickets
            'eventTicketObjects': [{
                'id': f'{issuer_id}.EVENT_OBJECT_SUFFIX',
                'classId': f'{issuer_id}.EVENT_CLASS_SUFFIX'
            }],

            # Boarding passes
            'flightObjects': [{
                'id': f'{issuer_id}.FLIGHT_OBJECT_SUFFIX',
                'classId': f'{issuer_id}.FLIGHT_CLASS_SUFFIX'
            }],

            # Generic passes
            'genericObjects': [{
                'id': f'{issuer_id}.GENERIC_OBJECT_SUFFIX',
                'classId': f'{issuer_id}.GENERIC_CLASS_SUFFIX'
            }],

            # Gift cards
            'giftCardObjects': [{
                'id': f'{issuer_id}.GIFT_CARD_OBJECT_SUFFIX',
                'classId': f'{issuer_id}.GIFT_CARD_CLASS_SUFFIX'
            }],

            # Loyalty cards
            'loyaltyObjects': [{
                'id': f'{issuer_id}.LOYALTY_OBJECT_SUFFIX',
                'classId': f'{issuer_id}.LOYALTY_CLASS_SUFFIX'
            }],

            # Offers
            'offerObjects': [{
                'id': f'{issuer_id}.OFFER_OBJECT_SUFFIX',
                'classId': f'{issuer_id}.OFFER_CLASS_SUFFIX'
            }],

            # Transit passes
            'transitObjects': [{
                'id': f'{issuer_id}.TRANSIT_OBJECT_SUFFIX',
                'classId': f'{issuer_id}.TRANSIT_CLASS_SUFFIX'
            }]
        }

        # Create the JWT claims
        claims = {
            'iss': self.credentials.service_account_email,
            'aud': 'google',
            'origins': ['www.example.com'],
            'typ': 'savetowallet',
            'payload': objects_to_add
        }

        # The service account credentials are used to sign the JWT
        signer = crypt.RSASigner.from_service_account_file(self.key_file_path)
        token = jwt.encode(signer, claims).decode('utf-8')

        print('Add to Google Wallet link')
        print(f'https://pay.google.com/gp/v/save/{token}')

        return f'https://pay.google.com/gp/v/save/{token}'

    # [END jwtExisting]

    # [START batch]
    def batch_create_objects(self, issuer_id: str, class_suffix: str):
        """Batch create Google Wallet objects from an existing class.

        The request body will be a multiline string. See below for information.

        https://cloud.google.com/compute/docs/api/how-tos/batch#example

        Args:
            issuer_id (str): The issuer ID being used for this request.
            class_suffix (str): Developer-defined unique ID for this pass class.
        """
        data = ''

        # Example: Generate three new pass objects
        for _ in range(3):
            # Generate a random object suffix
            object_suffix = str(uuid.uuid4()).replace('[^\\w.-]', '_')

            # See link below for more information on required properties
            # https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject
            batch_object = {
                'id': f'{issuer_id}.{object_suffix}',
                'classId': f'{issuer_id}.{class_suffix}',
                'state': 'ACTIVE',
                'heroImage': {
                    'sourceUri': {
                        'uri':
                            'https://farm4.staticflickr.com/3723/11177041115_6e6a3b6f49_o.jpg'
                    },
                    'contentDescription': {
                        'defaultValue': {
                            'language': 'en-US',
                            'value': 'Hero image description'
                        }
                    }
                },
                'textModulesData': [{
                    'header': 'Text module header',
                    'body': 'Text module body',
                    'id': 'TEXT_MODULE_ID'
                }],
                'linksModuleData': {
                    'uris': [{
                        'uri': 'http://maps.google.com/',
                        'description': 'Link module URI description',
                        'id': 'LINK_MODULE_URI_ID'
                    }, {
                        'uri': 'tel:6505555555',
                        'description': 'Link module tel description',
                        'id': 'LINK_MODULE_TEL_ID'
                    }]
                },
                'imageModulesData': [{
                    'mainImage': {
                        'sourceUri': {
                            'uri':
                                'http://farm4.staticflickr.com/3738/12440799783_3dc3c20606_b.jpg'
                        },
                        'contentDescription': {
                            'defaultValue': {
                                'language': 'en-US',
                                'value': 'Image module description'
                            }
                        }
                    },
                    'id': 'IMAGE_MODULE_ID'
                }],
                'barcode': {
                    'type': 'QR_CODE',
                    'value': 'QR code'
                },
                'locations': [{
                    'latitude': 37.424015499999996,
                    'longitude': -122.09259560000001
                }],
                'accountId': 'Account id',
                'accountName': 'Account name',
                'loyaltyPoints': {
                    'label': 'Points',
                    'balance': {
                        'int': 800
                    }
                }
            }

            data += '--batch_createobjectbatch\n'
            data += 'Content-Type: application/json\n\n'
            data += 'POST /walletobjects/v1/loyaltyObject/\n\n'

            data += json.dumps(batch_object) + '\n\n'

        data += '--batch_createobjectbatch--'

        # Invoke the batch API calls
        response = self.http_client.post(
            url='https://walletobjects.googleapis.com/batch',
            data=data,
            headers={
                # `boundary` is the delimiter between API calls in the batch request
                'Content-Type':
                    'multipart/mixed; boundary=batch_createobjectbatch'
            })

        print('Batch insert response')
        print(response.content.decode('UTF-8'))

    # [END batch]
