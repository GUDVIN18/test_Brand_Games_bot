from PIL import Image, ImageDraw, ImageFont
def edit_photo_func(url):    
    image_path = url

    # Открываем изображение
    img = Image.open(image_path)

    # Обрезаем изображение
    cropped_img = img.crop((100, 100, 300, 500))  # Пример: обрезаем изображение с координатами (100, 100) и размером 200x200

    # Добавляем текст "Привет"
    from PIL import ImageDraw 
    draw = ImageDraw.Draw(cropped_img)
    draw.text((10, 10), "Привет", fill=(255, 255, 255))  # Пример: координаты (10, 10)

    # Сохраняем измененное изображение
    edited_image_path = url
    cropped_img.save(edited_image_path)

    # Отправляем измененное изображение пользователю
    return open(edited_image_path, 'rb')