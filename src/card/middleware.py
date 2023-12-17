import os.path
import uuid

from fastapi import requests

from client.middleware import DemoLoyalty


async def save_static(file):
    img_path = os.path.join('static/img/', file.filename)

    with open(img_path, 'wb') as img_file:
        img_content = await file.read()
        img_file.write(img_content)


import os.path
import uuid

from client.middleware import DemoLoyalty


class CreateCard:
    def __init__(self):
        self.api = DemoLoyalty()
        self.issuer_id = '3388000000022253225'
        self.suffix = None  # Initialize self.suffix to None

    def generate_suffix(self):
        self.suffix = int(uuid.uuid4())  # Generate a new suffix

    @staticmethod
    def card_number():
        number1 = int(uuid.uuid4())
        number2 = int(uuid.uuid4())
        number3 = int(uuid.uuid4())
        number4 = int(uuid.uuid4())
        return f"{str(number1)[:4]} {str(number2)[:4]} {str(number3)[:4]} {str(number4)[:4]}"

    def create_class(self, corp_name, logo):
        if self.suffix is None:
            self.generate_suffix()  # Generate a new suffix if not already done

        self.api.create_class(
            self.issuer_id,
            self.suffix,
            top_text_content=corp_name,
            logo=logo
        )
        print(self.suffix)

    def get_card(self, corp_name, left_header, left_body,
                 right_header, right_body, logo, background,
                 client_first_name, client_last_name, color):
        if self.suffix is None:
            self.generate_suffix()  # Generate a new suffix if not already done

        url = self.api.create_jwt_new_objects(
            issuer_id=self.issuer_id,
            class_suffix=f'{uuid.uuid4()}',
            object_suffix=f'{uuid.uuid4()}',
            top_text_content=corp_name,
            text_left_header=left_header,
            text_left_content=left_body,
            text_right_header=right_header,
            text_right_content=right_body,
            logo=logo,
            background=background,
            client_name=f"{client_first_name} {client_last_name}",
            card_number=self.card_number(),
            color=color
        )
        return url

# test = CreateCard()
# test.create_class('21', 'https://platforma.oppti.me/_next/image?url=http%3A%2F%2F213.109.204.251%3A8000%2Fstatic%2Fimg%2F%C3%90%C2%A1%C3%90%C2%BD%C3%90%C2%B8%C3%90%C2%BC%C3%90%C2%BE%C3%90%C2%BA%2003.11.2023%20%C3%90%C2%B2%C3%82%C2%A017.05.jpeg&w=128&q=75')
# print(test.get_card('Делаем твою жизнь слаще', 'Бонусы', '576р', 'Владелец', 'Алексей К.',
#                    'https://i.ibb.co/KwX455z/C3-90-C2-A1-C3-90-C2-BD-C3-90-C2-B8-C3-90-C2-BC-C3-90-C2-BE-C3-90-C2-BA-2003.png',
#                    'https://i.ibb.co/kx4mbtT/logo.png', 'Sem',
#                     'Pem', '#ffffff'))
