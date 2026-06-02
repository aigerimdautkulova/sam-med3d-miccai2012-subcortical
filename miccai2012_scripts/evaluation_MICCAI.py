import argparse
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
import torch
from monai.metrics import DiceMetric, HausdorffDistanceMetric


labels = {
    1: "right_accumbens",
    2: "left_accumbens",
    3: "right_amygdala",
    4: "left_amygdala",
    5: "right_caudate",
    6: "left_caudate",
    7: "right_hippocampus",
    8: "left_hippocampus",
    9: "right_pallidum",
    10: "left_pallidum",
    11: "right_putamen",
    12: "left_putamen",
    13: "right_thalamus",
    14: "left_thalamus",
}


parser = argparse.ArgumentParser()
parser.add_argument("--pred_dir", type=Path, required=True)
parser.add_argument("--gt_dir", type=Path, required=True)
parser.add_argument("--out_dir", type=Path, required=True)
args = parser.parse_args()

args.out_dir.mkdir(parents=True, exist_ok=True)

dice_metric = DiceMetric(include_background=True, reduction="mean")
hd95_metric = HausdorffDistanceMetric(
    include_background=True,
    percentile=95,
    directed=False,
    reduction="mean",
)

results = []

for pred_path in sorted(args.pred_dir.glob("*.nii.gz")):
    subject = pred_path.name.replace(".nii.gz", "")
    gt_path = args.gt_dir / pred_path.name

    if not gt_path.exists():
        print(f"Missing ground truth for {subject}")
        continue

    print(f"Evaluating {subject}")

    pred_img = nib.load(pred_path)
    gt_img = nib.load(gt_path)

    pred = pred_img.get_fdata().astype(np.int16)
    gt = gt_img.get_fdata().astype(np.int16)
    spacing = gt_img.header.get_zooms()[:3]

    for label_id, label_name in labels.items():
        if not np.any(gt == label_id):
            continue

        pred_mask = pred == label_id
        gt_mask = gt == label_id

        pred_tensor = torch.tensor(pred_mask[None, None], dtype=torch.float32)
        gt_tensor = torch.tensor(gt_mask[None, None], dtype=torch.float32)

        dice = float(dice_metric(pred_tensor, gt_tensor).item())

        if pred_mask.sum() == 0 or gt_mask.sum() == 0:
            hd95 = np.nan
        else:
            hd95 = float(
                hd95_metric(pred_tensor, gt_tensor).item()
            )

        pred_volume = pred_mask.sum()
        gt_volume = gt_mask.sum()
        volume_similarity = 1 - abs(pred_volume - gt_volume) / (pred_volume + gt_volume)

        results.append({
            "subject": subject,
            "label": label_name,
            "dice": dice,
            "hd95": hd95,
            "volume_similarity": volume_similarity,
        })

df = pd.DataFrame(results)
df.to_csv(args.out_dir / "results_per_subject.csv", index=False)

summary = df.groupby("label")[["dice", "hd95", "volume_similarity"]].agg(["mean", "std"])
summary.to_csv(args.out_dir / "results_summary.csv")
# summary.to_excel(args.out_dir / "results_summary.xlsx")

print(summary)