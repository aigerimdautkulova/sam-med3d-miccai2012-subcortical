# MICCAI 2012 Scripts

This folder contains the MICCAI 2012-specific scripts added to this SAM-Med3D fork.

The scripts prepare selected subcortical structures from the public MICCAI 2012 Multi-Atlas Labeling Challenge dataset and evaluate segmentation predictions.

## Files

```text
miccai2012_scripts/
├── README.md
├── dataset.json
├── extract_labels.py
└── evaluation_MICCAI.py
```

## Dataset

Dataset page: https://www.neuromorphometrics.com/2012_MICCAI_Challenge_Data.html

The dataset is not included in this repository. Please download it from the official website and follow its usage terms.

After downloading and extracting the data, organize the files as:

```text
Task100_Miccai/
├── imagesTr/
│   ├── miccai_001_t1.nii
│   ├── miccai_002_t1.nii
│   └── ...
├── labelsTr/
│   ├── miccai_001.nii
│   ├── miccai_002.nii
│   └── ...
├── imagesTs/
│   ├── miccai_016_t1.nii
│   ├── miccai_017_t1.nii
│   └── ...
└── labelsTs/
    ├── miccai_016.nii
    ├── miccai_017.nii
    └── ...
```

## dataset.json

The file `dataset.json` is provided as an example dataset configuration.

For training or evaluation, copy it into the root of your prepared dataset folder:

```text
Task100_Miccai/
├── dataset.json
├── imagesTr/
├── labelsTr/
├── imagesTs/
└── labelsTs/
```

Example:

```bash
cp miccai2012_scripts/dataset.json /path/to/Task100_Miccai/dataset.json
```

## Label extraction

`extract_labels.py` extracts 14 selected subcortical structures and remaps them to consecutive labels from 1 to 14.

Selected structures:

- left / right accumbens
- left / right amygdala
- left / right caudate
- left / right hippocampus
- left / right pallidum
- left / right putamen
- left / right thalamus

Before running, edit `dataset_root` in `extract_labels.py` to point to your local MICCAI 2012 dataset folder.

Run:

```bash
python miccai2012_scripts/extract_labels.py
```

The script saves the processed images and labels as `.nii.gz` files:

```text
Task100_Miccai/
├── imagesTr/
│   ├── miccai_001_0000.nii.gz
│   ├── miccai_002_0000.nii.gz
│   └── ...
├── labelsTr/
│   ├── miccai_001.nii.gz
│   ├── miccai_002.nii.gz
│   └── ...
├── imagesTs/
│   ├── miccai_016_0000.nii.gz
│   ├── miccai_017_0000.nii.gz
│   └── ...
└── labelsTs/
    ├── miccai_016.nii.gz
    ├── miccai_017.nii.gz
    └── ...
```

## Evaluation

`evaluation_MICCAI.py` evaluates predicted segmentations against ground-truth labels.

Predictions and ground-truth labels should have matching filenames:

```text
predictions/
├── miccai_016.nii.gz
├── miccai_017.nii.gz
└── ...

labelsTs/
├── miccai_016.nii.gz
├── miccai_017.nii.gz
└── ...
```

Run:

```bash
python miccai2012_scripts/evaluation_MICCAI.py \
  --pred_dir predictions \
  --gt_dir labelsTs \
  --out_dir results
```

The script saves:

```text
results/
├── results_per_subject.csv
└── results_summary.csv
```

Metrics:

- Dice coefficient
- 95th percentile Hausdorff distance
- volume similarity

## Note

These scripts are independent additions for MICCAI 2012 experiments and do not include the MICCAI dataset, trained models, private data, or confidential implementation details.
