import json
import os
import zipfile
import aiohttp
import requests
from loguru import logger

from apple.utils import hex_to_rgb, resize_and_save_image_async

from .test import test


class AppleCard:
    def __init__(self):
        self.url = 'http://213.109.204.251:8010/api/'

    @staticmethod
    async def generate_cert(client_id):
        path = os.path.join(os.getcwd(), "apple", "client", client_id)
        path_to_cert = os.path.join(path, "certs")
        logger.info(f"Инициализирую генерацию сертификата для клиента {client_id}")
        try:
            if not os.path.isdir(path):
                logger.info(f"Создается клиент: {client_id} в папке {path}")
                os.mkdir(path)
                if not os.path.isdir(path_to_cert):
                    logger.info("Создаем сертификаты")
                    os.mkdir(path_to_cert)
                    os.system(
                        f"openssl genrsa -out {os.path.join(path_to_cert, 'signerKey.pem')} -passout pass:PASSPHRASE 2048")
                    os.system(
                        f"openssl req -new -key {os.path.join(path_to_cert, 'signerKey.pem')} -out {os.path.join(path_to_cert, 'request.certSigningRequest')} -subj '/C=US/ST=New York/L=New York/O=Your Organization/OU=Your Unit/CN={client_id}'")
                    test(client_id)
                    return os.path.join(path_to_cert, "request.certSigningRequest")
            else:
                logger.info("Клиент уже существует")
                return os.path.join(path_to_cert, "request.certSigningRequest")
        except Exception as error:
            logger.error(error)

    async def upload_certifi(self, team_id, pass_identifier, client_id):
        try:
            path = os.path.join(os.getcwd(), f"apple/client/{client_id}/certs/")
            path_save = os.path.join(os.getcwd(), f"apple/client/{client_id}/")
            os.system(
                f"openssl x509 -inform DER -outform PEM -in {os.path.join(path, 'pass.cer')} -out {os.path.join(path, 'signerCert.pem')}")
            os.system(
                f"openssl x509 -inform DER -outform PEM -in {os.path.join(path, 'pass.cer')} -out {os.path.join(path, 'wwdr.pem')}")
            os.system(
                f"openssl rsa -in {os.path.join(path, 'signerKey.pem')} -out {os.path.join(path, 'signerKey_no_passphrase.pem')}")

            with zipfile.ZipFile(os.path.join(path_save, f"{client_id}.zip"), 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Определите относительный путь файла внутри архива
                        rel_path = os.path.relpath(file_path, path)
                        zipf.write(file_path, rel_path)
        except Exception as error:
            logger.error(error)

        zip_name = os.path.join(os.getcwd(), f"apple/client/{client_id}/", f"{client_id}.zip")
        query = {'file': open(zip_name, 'rb')}
        response = requests.post(self.url + f"certs/save-single-cert/{client_id}/{team_id}/{pass_identifier}",
                                 files=query)
        print(response.json())
        logger.info('Сертификат загружен и готов к работе')

    async def create_card(self, client_id, team_id, pass_identifier, pass_sn,
                          company_name, logo_text, logo_description, text_left_header, text_left_content,
                          text_right_header, text_right_content, color_background, color_text):
        # Создаем словарь с данными для пасса
        pass_data = {
            "formatVersion": 1,
            "passTypeIdentifier": pass_identifier,
            "serialNumber": pass_sn,
            "teamIdentifier": team_id,
            "webServiceURL": "https://usicufu.shop/",
            "authenticationToken": "vxwxd7J8AlNNFPS8k0a0FfUFtq0ewzFdc",
            "locations": [
                {
                    "longitude": -122.3748889,
                    "latitude": 37.6189722
                }
            ],
            "barcode": {
                "message": "123456789",
                "format": "PKBarcodeFormatPDF417",
                "messageEncoding": "iso-8859-1"
            },
            "organizationName": company_name,
            "description": company_name,
            "foregroundColor": f"rgb{hex_to_rgb(color_text)}",
            "backgroundColor": f"rgb{hex_to_rgb(color_background)}",
            "storeCard": {
                "headerFields": [
                    {
                        "key": "staffNumber",
                        "label": logo_text,
                        "value": logo_description
                    }
                ],
                "auxiliaryFields": [
                    {
                        "key": "deal",
                        "label": text_left_header,
                        "value": text_left_content
                    },
                    {
                        "key": "wel",
                        "label": text_right_header,
                        "value": text_right_content
                    }
                ]
            }
        }

        # Сохраняем словарь в файл в формате JSON
        base_path = os.path.join(os.getcwd(), 'apple', 'card', 'default', 'pass.json')
        with open(base_path, 'w') as json_file:
            json.dump(pass_data, json_file, indent=4)

        logger.info('JSON данные сохранены в pass.json')
        path = os.path.join(os.getcwd(), 'apple', 'card', 'default', '')
        save_path = os.path.join(os.getcwd(), 'apple', 'client', client_id, '')
        with zipfile.ZipFile(os.path.join(save_path, f'{pass_sn}_card.zip'), 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Определите относительный путь файла внутри архива
                    rel_path = os.path.relpath(file_path, path)
                    zipf.write(file_path, rel_path)

        zip_name = os.path.join(os.getcwd(), 'apple', 'client', client_id, f'{pass_sn}_card.zip')
        query = {'file': open(zip_name, 'rb')}
        data = requests.post(self.url + f"passes/save-single-pass/{client_id}/{team_id}/{pass_identifier}/{pass_sn}", files=query)
        print(data.json())
        logger.info('Архив создан')

    async def update_card(self, client_id, team_id, pass_identifier, pass_sn,
                          company_name, logo_text, logo_description, text_left_header, text_left_content,
                          text_right_header, text_right_content, color_background, color_text, logo, background, icon):
        # Создаем словарь с данными для пасса
        pass_data = {
            "formatVersion": 1,
            "passTypeIdentifier": pass_identifier,
            "serialNumber": pass_sn,
            "teamIdentifier": team_id,
            "webServiceURL": "https://usicufu.shop/",
            "authenticationToken": "vxwxd7J8AlNNFPS8k0a0FfUFtq0ewzFdc",
            "locations": [
                {
                    "latitude": 37.331,
                    "longitude": -122.029,
                }
            ],
            "barcode": {
                "message": "123456789",
                "format": "PKBarcodeFormatPDF417",
                "messageEncoding": "iso-8859-1"
            },
            "organizationName": company_name,
            "description": company_name,
            "foregroundColor": f"rgb{hex_to_rgb(color_text)}",
            "backgroundColor": f"rgb{hex_to_rgb(color_background)}",
            "storeCard": {
                "headerFields": [
                    {
                        "key": "staffNumber",
                        "label": logo_text,
                        "value": logo_description
                    }
                ],
                "auxiliaryFields": [
                    {
                        "key": "deal",
                        "label": text_left_header,
                        "value": text_left_content
                    },
                    {
                        "key": "wel",
                        "label": text_right_header,
                        "value": text_right_content
                    }
                ]
            }
        }

        # Сохраняем словарь в файл в формате JSON
        update_path = os.path.join(os.getcwd(), 'apple', 'card', f'{client_id}')
        if not os.path.isdir(update_path):
            print('Мы тут')
            os.mkdir(update_path)
            base_path = os.path.join(os.getcwd(), 'apple', 'card', f'{client_id}', 'pass.json')
            await resize_and_save_image_async(logo, (90, 80), 'logo.png', client_id)
            await resize_and_save_image_async(background, (312, 123), 'strip.png', client_id)
            await resize_and_save_image_async(background, (624, 245), 'strip@2x.png', client_id)
            await resize_and_save_image_async(icon, (35, 35), 'icon.png', client_id)
            await resize_and_save_image_async(icon, (69, 69), 'icon@2x.png', client_id)

            with open(base_path, 'w') as json_file:
                json.dump(pass_data, json_file, indent=4)

            logger.info('JSON данные сохранены в pass.json')
            path = os.path.join(os.getcwd(), 'apple', 'card', f'{client_id}', '')
            save_path = os.path.join(os.getcwd(), 'apple', 'client', client_id, '')
            with zipfile.ZipFile(os.path.join(save_path, f'{client_id}_card_update.zip'), 'w',
                                 zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Определите относительный путь файла внутри архива
                        rel_path = os.path.relpath(file_path, path)
                        zipf.write(file_path, rel_path)

            zip_name = os.path.join(os.getcwd(), 'apple', 'client', client_id, f'{client_id}_card_update.zip')
            url = f"{self.url}passes/save-single-pass/{client_id}/{team_id}/{pass_identifier}/{pass_sn}"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={'file': open(zip_name, 'rb')}) as response:
                    logger.info('Архив обновлен впервые')
                    return await response.text()
        else:
            print('Сохраняем картинки')
            base_path = os.path.join(os.getcwd(), 'apple', 'card', f'{client_id}', 'pass.json')
            await resize_and_save_image_async(logo, (90, 80), 'logo.png', client_id)
            await resize_and_save_image_async(background, (312, 123), 'strip.png', client_id)
            await resize_and_save_image_async(background, (624, 245), 'strip@2x.png', client_id)
            await resize_and_save_image_async(icon, (35, 35), 'icon.png', client_id)
            await resize_and_save_image_async(icon, (69, 69), 'icon@2x.png', client_id)
            print('Картинки сохранены')
            with open(base_path, 'w') as json_file:
                json.dump(pass_data, json_file, indent=4)

            logger.info('JSON данные сохранены в pass.json')
            path = os.path.join(os.getcwd(), 'apple', 'card', f'{client_id}', '')
            save_path = os.path.join(os.getcwd(), 'apple', 'client', client_id, '')
            with zipfile.ZipFile(os.path.join(save_path, f'{client_id}_card_update.zip'), 'w',
                                 zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Определите относительный путь файла внутри архива
                        rel_path = os.path.relpath(file_path, path)
                        zipf.write(file_path, rel_path)

            zip_name = os.path.join(os.getcwd(), 'apple', 'client', client_id, f'{client_id}_card_update.zip')
            url = f"{self.url}passes/save-single-pass/{client_id}/{team_id}/{pass_identifier}/{pass_sn}"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={'file': open(zip_name, 'rb')}) as response:
                    logger.info('Архив обновлен')
                    return await response.text()

    async def update_push(self, client_id, team_id, pass_identifier, pass_sn,
                          company_name, logo_text, logo_description, text_left_header, text_left_content,
                          text_right_header, text_right_content, color_background, color_text, logo, background, icon,
                          my_dict):
        # Создаем словарь с данными для пасса
        pass_data = {
            "formatVersion": 1,
            "passTypeIdentifier": pass_identifier,
            "serialNumber": pass_sn,
            "teamIdentifier": team_id,
            "webServiceURL": "https://usicufu.shop/",
            "authenticationToken": "vxwxd7J8AlNNFPS8k0a0FfUFtq0ewzFdc",
            "barcode": {
                "message": "123456789",
                "format": "PKBarcodeFormatPDF417",
                "messageEncoding": "iso-8859-1"
            },
            "locations": [
                {
                    "longitude": -122.3748889,
                    "latitude": 37.6189722
                }
            ],
            "organizationName": company_name,
            "description": company_name,
            "foregroundColor": f"rgb{hex_to_rgb(color_text)}",
            "backgroundColor": f"rgb{hex_to_rgb(color_background)}",
            "storeCard": {
                "headerFields": [
                    {
                        "key": "staffNumber",
                        "label": logo_text,
                        "value": logo_description
                    }
                ],
                "auxiliaryFields": [
                    {
                        "key": "deal",
                        "label": text_left_header,
                        "value": text_left_content
                    },
                    {
                        "key": "wel",
                        "label": text_right_header,
                        "value": text_right_content
                    }
                ]
            }
        }
        pass_data.update(my_dict)
        print(pass_data)
        # Сохраняем словарь в файл в формате JSON
        update_path = os.path.join(os.getcwd(), 'apple', 'card', f'{client_id}')
        if not os.path.isdir(update_path):
            os.mkdir(update_path)
            base_path = os.path.join(os.getcwd(), 'apple', 'card', f'{client_id}', 'pass.json')
            await resize_and_save_image_async(logo, (90, 80), 'logo.png', client_id)
            await resize_and_save_image_async(background, (312, 123), 'strip.png', client_id)
            await resize_and_save_image_async(background, (624, 245), 'strip@2x.png', client_id)
            await resize_and_save_image_async(icon, (35, 35), 'icon.png', client_id)
            await resize_and_save_image_async(icon, (69, 69), 'icon@2x.png', client_id)
            with open(base_path, 'w') as json_file:
                json.dump(pass_data, json_file, indent=4)
                json_file.close()

            logger.info('JSON данные сохранены в pass.json')
            path = os.path.join(os.getcwd(), 'apple', 'card', f'{client_id}', '')
            save_path = os.path.join(os.getcwd(), 'apple', 'client', client_id, '')
            with zipfile.ZipFile(os.path.join(save_path, f'{client_id}_card_update.zip'), 'w',
                                 zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Определите относительный путь файла внутри архива
                        rel_path = os.path.relpath(file_path, path)
                        zipf.write(file_path, rel_path)
                        zipf.close()

            zip_name = os.path.join(os.getcwd(), 'apple', 'client', client_id, f'{client_id}_card_update.zip')
            url = f"{self.url}passes/save-single-pass/{client_id}/{team_id}/{pass_identifier}/{pass_sn}"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={'file': open(zip_name, 'rb')}) as response:
                    logger.info('Архив обновлен впервые')
                    return await response.text()
        else:
            base_path = os.path.join(os.getcwd(), 'apple', 'card', f'{client_id}', 'pass.json')
            await resize_and_save_image_async(logo, (90, 80), 'logo.png', client_id)
            await resize_and_save_image_async(background, (312, 123), 'strip.png', client_id)
            await resize_and_save_image_async(background, (624, 245), 'strip@2x.png', client_id)
            await resize_and_save_image_async(icon, (35, 35), 'icon.png', client_id)
            await resize_and_save_image_async(icon, (69, 69), 'icon@2x.png', client_id)
            with open(base_path, 'w') as json_file:
                json.dump(pass_data, json_file, indent=4)
                json_file.close()
            logger.info('JSON данные сохранены в pass.json')
            path = os.path.join(os.getcwd(), 'apple', 'card', f'{client_id}', '')
            save_path = os.path.join(os.getcwd(), 'apple', 'client', client_id, '')
            with zipfile.ZipFile(os.path.join(save_path, f'{client_id}_card_update.zip'), 'w',
                                 zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Определите относительный путь файла внутри архива
                        rel_path = os.path.relpath(file_path, path)
                        zipf.write(file_path, rel_path)
            zipf.close()

            zip_name = os.path.join(os.getcwd(), 'apple', 'client', client_id, f'{client_id}_card_update.zip')
            url = f"{self.url}passes/save-single-pass/{client_id}/{team_id}/{pass_identifier}/{pass_sn}"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={'file': open(zip_name, 'rb')}) as response:
                    logger.info('Архив обновлен')
                    return await response.text()
