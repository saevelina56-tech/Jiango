from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


def process_image(image_field, max_size=(800, 800), thumb_size=(200, 200)):
    img = Image.open(image_field)
    img = img.convert('RGB')

    img.thumbnail(max_size, Image.LANCZOS)
    main_io = BytesIO()
    img.save(main_io, format='JPEG', quality=85)
    main_file = ContentFile(main_io.getvalue())

    thumb = img.copy()
    thumb.thumbnail(thumb_size, Image.LANCZOS)
    thumb_io = BytesIO()
    thumb.save(thumb_io, format='JPEG', quality=80)
    thumb_file = ContentFile(thumb_io.getvalue())

    return main_file, thumb_file