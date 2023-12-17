import aiohttp
from io import BytesIO
from PIL import Image


class ImageData:
    def __init__(self, url):
        self.url = url

    async def fetch_image(self, session):
        try:
            async with session.get(self.url) as response:
                response.raise_for_status()  # Check for a successful request
                return await response.read()

        except Exception as error:
            raise Exception(f"Error fetching the image: {error}")

    async def upload_image(self, image_data, size):
        try:
            async with aiohttp.ClientSession() as session:
                image = Image.open(BytesIO(image_data))
                image = image.resize(size, Image.BILINEAR)
                with BytesIO() as image_bytes:
                    image.save(image_bytes, format='PNG')
                    image_data = image_bytes.getvalue()

                form_data = aiohttp.FormData()
                form_data.add_field('image', image_data, filename='image.png', content_type='image/png')

                async with session.post(
                        'https://api.imgbb.com/1/upload',
                        params={'key': '8ffb2472c22a15afd7a9349cb1e50465'},
                        data=form_data
                ) as response:
                    data = await response.json()
                    print(data)
                    return data['data']['url']

        except Exception as error:
            raise Exception(f"Error uploading the image: {error}")

    async def crop_and_upload_image(self, size):
        try:
            async with aiohttp.ClientSession() as session:
                image_data = await self.fetch_image(session)
                return await self.upload_image(image_data, size)

        except Exception as error:
            raise Exception(f"Error cropping and uploading the image: {error}")
