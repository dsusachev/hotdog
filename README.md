![Tests](https://github.com/dsusachev/hotdog/raw/badges/tests.svg)
![Coverage](https://github.com/dsusachev/hotdog/raw/badges/coverage.svg)

AI based program to recognize bakery products.

* Code is written and placed in the src/ folder.
* Tests are written and placed in the test/ folder.
* All tests pass successfully.
* Code follows agreed style guidelines and has been reviewed (if required).
* Task is marked as completed in the tracking system (e.g., Jira, Trello).

## Architecture
![Схема системы](doc/backend/hotdog_system_architecture.svg)

---

## Запуск проекта

### Первый запуск (один раз)

**1. Установить программы** (если ещё нет):
- Python 3.11+ → https://python.org/downloads
- Node.js 20+ → https://nodejs.org
- Git → https://git-scm.com

**2. Скачать проект:**
```bash
git clone https://github.com/dsusachev/hotdog.git
cd hotdog
```

**3. Установить зависимости:**
```bash
pip install -r requirements.txt          # backend
pip install -r ml/requirements.txt       # ML-сервис (torch и т.д.) — для реальной модели
cd src/front && npm install && cd ../..
```
> Без `ml/requirements.txt` сайт тоже запустится, но ML будет работать в режиме **заглушки** (фиксированный ответ).

**4. Создать файл `.env`:**
```bash
cp env.example .env
```
Открыть `.env` и вставить данные подключения к БД — спросить у DB-разработчика (Supabase credentials).

---

### Запуск (каждый раз)

```bash
python start.py
```

Откроется:
- Фронтенд → http://localhost:3000
- Backend API → http://localhost:8000
- ML-сервис → http://localhost:8001

Остановка — **Ctrl+C**

> **Модель скачивается сама.** При первом запуске `start.py` подтянет артефакт
> `resnet50_v1_20260519.pt` (~90 МБ) из [GitHub Release `models-v1`](https://github.com/dsusachev/hotdog/releases/tag/models-v1)
> в `ml/artifacts/` — никакого Google Drive вручную. Можно скачать заранее:
> ```bash
> python ml/scripts/download_model.py            # resnet50 (по умолчанию)
> python ml/scripts/download_model.py --model efficientnet   # лёгкая модель, 16 МБ
> ```
> Если torch/модель недоступны — ML работает в режиме заглушки, сайт остаётся рабочим.

---

### Обновление (когда вышли новые изменения)

```bash
git pull
pip install -r requirements.txt
cd src/front && npm install && cd ../..
python start.py
```
