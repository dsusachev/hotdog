# Final ML Metrics

**Model:** `resnet50_v1_20260519.pt`

## Threshold (tuned on val)
| threshold | coverage | selective accuracy | target met |
|-----------|----------|--------------------|------------|
| 0.39 | 89.53% | 95.09% | True |

## Summary table

| split | n | top-1 | top-3 | macro-F1 (all) | macro-F1 (present) | weighted-F1 |
|-------|---|-------|-------|----------------|---------------------|-------------|
| val | 296 | 91.89% | 95.95% | 73.99% | 85.99% | 91.28% |
| test | 2485 | 91.35% | 97.71% | 86.86% | 86.86% | 90.85% |
| ood_iconic | 81 | 74.07% | 85.19% | 60.84% | 60.84% | 69.93% |
| own_mini ⚠️ | 26 | 30.77% | 61.54% | 5.00% | 35.81% | 34.91% |

> ⚠️ **own_mini**: Only 6 out of 43 classes are covered; accuracy numbers are not representative of overall model quality.

## Split: `val`

- Samples: **296**
- Classes present: 37 / 43
- Top-1 accuracy: **91.89%**
- Top-3 accuracy: **95.95%**
- Macro-F1 (all 43 classes): 73.99%
- Macro-F1 (present only): 85.99%
- Weighted-F1: 91.28%
- Missing classes: Nectarine, Papaya, Plum, Sour-Milk, Soy-Milk, Garlic

**Threshold analysis** (coverage/selective-accuracy at artifact threshold t=0.39):
- Coverage: 89.53% (265/296 samples)
- Selective accuracy: 95.09%

**10 lowest-recall classes:**

| class | precision | recall | F1 | support |
|-------|-----------|--------|----|---------|
| Lemon | 0.000 | 0.000 | 0.000 | 5 |
| Mango | 0.000 | 0.000 | 0.000 | 3 |
| Ginger | 1.000 | 0.500 | 0.667 | 4 |
| Satsumas | 0.600 | 0.600 | 0.600 | 5 |
| Asparagus | 1.000 | 0.600 | 0.750 | 5 |
| Onion | 1.000 | 0.600 | 0.750 | 5 |
| Kiwi | 1.000 | 0.800 | 0.889 | 5 |
| Orange | 1.000 | 0.800 | 0.889 | 5 |
| Peach | 1.000 | 0.800 | 0.889 | 5 |
| Pear | 1.000 | 0.800 | 0.889 | 5 |

## Split: `test`

- Samples: **2485**
- Classes present: 43 / 43
- Top-1 accuracy: **91.35%**
- Top-3 accuracy: **97.71%**
- Macro-F1 (all 43 classes): 86.86%
- Macro-F1 (present only): 86.86%
- Weighted-F1: 90.85%

**Threshold analysis** (coverage/selective-accuracy at artifact threshold t=0.39):
- Coverage: 93.60% (2326/2485 samples)
- Selective accuracy: 94.02%

**10 lowest-recall classes:**

| class | precision | recall | F1 | support |
|-------|-----------|--------|----|---------|
| Lime | 0.857 | 0.200 | 0.324 | 30 |
| Lemon | 0.846 | 0.268 | 0.407 | 41 |
| Ginger | 1.000 | 0.333 | 0.500 | 15 |
| Mango | 0.750 | 0.484 | 0.588 | 31 |
| Nectarine | 0.679 | 0.543 | 0.603 | 35 |
| Orange | 0.547 | 0.625 | 0.583 | 56 |
| Passion-Fruit | 0.531 | 0.630 | 0.576 | 27 |
| Cucumber | 1.000 | 0.630 | 0.773 | 27 |
| Satsumas | 0.712 | 0.691 | 0.701 | 68 |
| Red-Grapefruit | 0.413 | 0.765 | 0.536 | 34 |

## Split: `ood_iconic`

- Samples: **81**
- Classes present: 43 / 43
- Top-1 accuracy: **74.07%**
- Top-3 accuracy: **85.19%**
- Macro-F1 (all 43 classes): 60.84%
- Macro-F1 (present only): 60.84%
- Weighted-F1: 69.93%

**Threshold analysis** (coverage/selective-accuracy at artifact threshold t=0.39):
- Coverage: 79.01% (64/81 samples)
- Selective accuracy: 85.94%

**10 lowest-recall classes:**

| class | precision | recall | F1 | support |
|-------|-----------|--------|----|---------|
| Kiwi | 0.000 | 0.000 | 0.000 | 1 |
| Lemon | 0.000 | 0.000 | 0.000 | 1 |
| Lime | 0.000 | 0.000 | 0.000 | 1 |
| Mango | 0.000 | 0.000 | 0.000 | 1 |
| Nectarine | 0.000 | 0.000 | 0.000 | 1 |
| Orange | 0.000 | 0.000 | 0.000 | 1 |
| Papaya | 0.000 | 0.000 | 0.000 | 1 |
| Passion-Fruit | 0.000 | 0.000 | 0.000 | 1 |
| Peach | 0.000 | 0.000 | 0.000 | 1 |
| Pear | 0.000 | 0.000 | 0.000 | 3 |

## Split: `own_mini`

- Samples: **26**
- Classes present: 6 / 43
- Top-1 accuracy: **30.77%**
- Top-3 accuracy: **61.54%**
- Macro-F1 (all 43 classes): 5.00%
- Macro-F1 (present only): 35.81%
- Weighted-F1: 34.91%
- Missing classes: Avocado, Kiwi, Lemon, Lime, Mango, Melon, Nectarine, Orange, Papaya, Passion-Fruit, Peach, Pineapple, Plum, Pomegranate, Red-Grapefruit, Satsumas, Oatghurt, Oat-Milk, Sour-Cream, Sour-Milk, Soyghurt, Soy-Milk, Asparagus, Aubergine, Cabbage, Carrots, Cucumber, Garlic, Ginger, Leek, Mushroom, Onion, Pepper, Potato, Red-Beet, Tomato, Zucchini

**Threshold analysis** (coverage/selective-accuracy at artifact threshold t=0.39):
- Coverage: 34.62% (9/26 samples)
- Selective accuracy: 33.33%

**10 lowest-recall classes:**

| class | precision | recall | F1 | support |
|-------|-----------|--------|----|---------|
| Milk | 0.000 | 0.000 | 0.000 | 4 |
| Yoghurt | 0.000 | 0.000 | 0.000 | 5 |
| Juice | 0.167 | 0.200 | 0.182 | 5 |
| Pear | 1.000 | 0.333 | 0.500 | 3 |
| Banana | 1.000 | 0.500 | 0.667 | 4 |
| Apple | 0.800 | 0.800 | 0.800 | 5 |
