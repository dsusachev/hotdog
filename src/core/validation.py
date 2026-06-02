import io

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from src.core.config import settings


def validateImageFile(file: UploadFile, imageBytes: bytes) -> None:
    """
    Полная валидация загружаемого изображения:
    1. Наличие файла и имени
    2. Расширение файла (JPG/PNG)
    3. Пустой файл
    4. Размер файла (макс. 5 МБ)
    5. Повреждённое изображение
    """

    # 1. Проверка наличия файла
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided",
        )

    # 2. Проверка расширения
    extension = file.filename.split(".")[-1].lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Поддерживаются только JPG и PNG",
        )

    # 3. Проверка на пустой файл
    if len(imageBytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty",
        )

    # 4. Проверка размера
    maxBytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(imageBytes) > maxBytes:
        raise HTTPException(
            status_code=400,
            detail=f"Файл не должен превышать {settings.MAX_FILE_SIZE_MB} МБ",
        )

    # 5. Проверка на повреждённое изображение
    try:
        image = Image.open(io.BytesIO(imageBytes))
        image.verify()  # Проверяет целостность файла
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="File is not a valid image",
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Image file is corrupted or damaged",
        )
