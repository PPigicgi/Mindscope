# Evaluation notes

> **Warning:** These are internal experimental results, not clinical validation. They are not diagnostic claims and have not been externally or prospectively validated.

The primary machine-readable benchmark outputs are published in [`results/verified_metrics.csv`](../results/verified_metrics.csv). Participant-level material is not redistributed.

| Track | Model | Test n | Positives / negatives | Threshold | ROC-AUC | Balanced accuracy | F1 | Precision | Recall | Specificity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dementia audio | HuBERT + XGBoost | 412 | 183 / 229 | 0.39 | 0.76515 | 0.72804 | 0.71212 | 0.66197 | 0.77049 | 0.68559 |
| Depression audio | HuBERT + MLP | 56 | 30 / 26 | 0.05 | 0.58462 | 0.57949 | 0.72500 | 0.58000 | 0.96667 | 0.19231 |
| Depression video | OpenFace + Mamba-3 | 56 | 30 / 26 | 0.81 | 0.59872 | 0.55897 | 0.64706 | 0.57895 | 0.73333 | 0.38462 |

## Threshold confusion matrices

### Dementia audio (threshold 0.39)

| Actual / predicted | Negative | Positive |
| --- | ---: | ---: |
| Negative | TN 157 | FP 72 |
| Positive | FN 42 | TP 141 |

### Depression audio (threshold 0.05)

| Actual / predicted | Negative | Positive |
| --- | ---: | ---: |
| Negative | TN 5 | FP 21 |
| Positive | FN 1 | TP 29 |

### Depression video (threshold 0.81)

| Actual / predicted | Negative | Positive |
| --- | ---: | ---: |
| Negative | TN 10 | FP 16 |
| Positive | FN 8 | TP 22 |

## How to read these results

The dementia audio result is an internal 412-sample held-out test: ROC-AUC 0.765, balanced accuracy 0.728, and F1 0.712. Its threshold was selected on development data.

The depression audio result is an internal 56-session test: ROC-AUC 0.585 and balanced accuracy 0.579. Its recall of 0.967 came with specificity of 0.192, so F1 alone is misleading.

The depression video result is an internal 56-session test: ROC-AUC 0.599, balanced accuracy 0.559, and F1 0.647. These metrics were recomputed from predictions, and the threshold was selected on a development split.

ROC-AUC describes ranking across thresholds, while balanced accuracy gives equal weight to sensitivity and specificity when classes are uneven. F1 summarizes the positive-class precision/recall trade-off; recall and specificity make the false-negative and false-positive trade-offs visible. Showing all of them together avoids presenting a single threshold-dependent score as the whole result.

## Important evaluation caveats

- Both HuBERT audio scripts fit their scaler and classifier on train plus development samples, then use in-sample development predictions for threshold selection. The test set remains separate, but this threshold selection is not leakage-free.
- Archived tables selected or sorted models by test metrics. Therefore, the selected-model scores are exploratory rather than unbiased final estimates.
- The video provenance has a reproducible prediction file supporting ROC-AUC 0.59872. A historical reported video AUC is unsupported/manual, and the 31-versus-49 feature contract needs artifact validation.
- YOLO evaluation is validation-only (230 images) with a random image-level split, no independent test set, and no identity or source grouping. Its metrics should not be headline results.
- No confidence intervals or external prospective validation are available.
