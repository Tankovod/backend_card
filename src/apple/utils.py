import os
from io import BytesIO
from PIL import Image
import aiohttp


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


async def resize_and_save_image_async(image_url, target_size, filename, client_id):
    try:
        print(image_url)
        # Загрузите изображение по URL с использованием aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                image_data = await response.read()

        image = Image.open(BytesIO(image_data))

        path_save = os.path.join(os.getcwd(), 'apple', 'card', client_id, filename)

        # Измените размер изображения
        image = image.resize(target_size)

        # Сохраните изображение в текущей директории
        image.save(path_save)
        print(f"Изображение успешно изменено и сохранено в {path_save}")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
