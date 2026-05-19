# Own mini test set (task #45)

Folder layout for our team's photos used to evaluate domain shift on
Russian-store products (ml_aproach.md §3.3).

## Target

5–10 photos per class (10 classes), 6 team members × ~30 photos = **~180 total**.

## Classes (must match folder names exactly)

Fruits:    Apple, Banana, Orange, Pear
Vegetables: Tomato, Pepper, Potato
Packaged:  Milk, Juice, Yoghurt

Names are case-sensitive and must equal the Coarse Class Name column in
ml/dataset/GroceryStoreDataset/dataset/classes.csv. The loader raises
on unknown folders — silent label mismatches are worse than a crash.

## File requirements

- Format: JPG / PNG / WEBP (HEIC also accepted)
- Subject: one product clearly in frame, real-world conditions
- Russian-store products preferred for the packaged categories — that is
  the whole point of this set
- Filename: anything, the loader sorts by name
- Avoid duplicates between team members (one team member can name files
  with their initials, e.g. `vk_001.jpg`)

## How to add photos

Drop files into the right class folder. Run from repo root:

    ml/.venv/bin/python ml/scripts/sanity_check_own_set.py

(verifies all files load, prints per-class counts).

## Optional: download by URL

If a class is undercovered, point-wise download from open sources:

1. Build a CSV `urls.csv` with header `class_name,url`.
2. Run:
       ml/.venv/bin/python ml/scripts/download_urls.py --csv urls.csv

Recommended sources for Russian products:
- https://world.openfoodfacts.org (open API, RU products available)
- Direct image URLs from product pages on sites that allow direct linking

DO NOT scrape commercial sites that forbid automation (Yandex.Eda,
Wildberries, Ozon, etc.) — it is fragile, TOS-violating, and overkill
for a 180-photo set we can take by hand.
