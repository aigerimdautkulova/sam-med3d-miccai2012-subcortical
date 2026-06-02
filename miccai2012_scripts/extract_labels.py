"""
extract_labels.py

Prepare selected subcortical labels from the MICCAI 2012 multi-atlas labeling
challenge dataset in nnU-Net format.

The original MICCAI label maps contain many anatomical labels. This script
extracts 14 subcortical structures and remaps them to consecutive labels
from 1 to 14, while keeping background as 0.

Selected structures:
    1   Right accumbens
    2   Left accumbens
    3   Right amygdala
    4   Left amygdala
    5   Right caudate
    6   Left caudate
    7   Right hippocampus
    8   Left hippocampus
    9   Right pallidum
    10  Left pallidum
    11  Right putamen
    12  Left putamen
    13  Right thalamus
    14  Left thalamus

Original MICCAI labels:
    Left/right thalamus:     60 / 59
    Left/right caudate:      37 / 36
    Left/right putamen:      58 / 57
    Left/right pallidum:     56 / 55
    Left/right hippocampus:  48 / 47
    Left/right amygdala:     32 / 31
    Left/right accumbens:    30 / 23

Expected input files:
    imagesTr/miccai_001_t1.nii
    labelsTr/miccai_001.nii

Output files:
    imagesTr/miccai_001_0000.nii.gz
    labelsTr/miccai_001.nii.gz

nnU-Net convention:
    - Images use the modality suffix: _0000.nii.gz
    - Labels do not use the modality suffix.
"""

from pathlib import Path

import nibabel as nib
import numpy as np


# Some MICCAI NIfTI files may contain slightly non-standard quaternion values.
# This relaxes nibabel's quaternion validation threshold.
nib.Nifti1Header.quaternion_threshold = -1e-6


# Mapping from original MICCAI/Neuromorphometrics label IDs
# to new consecutive labels used for this segmentation task.
LABEL_MAPPING = {
    23: 1,   # Right accumbens
    30: 2,   # Left accumbens

    31: 3,   # Right amygdala
    32: 4,   # Left amygdala

    36: 5,   # Right caudate
    37: 6,   # Left caudate

    47: 7,   # Right hippocampus
    48: 8,   # Left hippocampus

    55: 9,   # Right pallidum
    56: 10,  # Left pallidum

    57: 11,  # Right putamen
    58: 12,  # Left putamen

    59: 13,  # Right thalamus
    60: 14,  # Left thalamus
}


def remap_labels(label_data: np.ndarray) -> np.ndarray:
    """
    Remap the original MICCAI labels to 14 selected subcortical labels.

    Parameters
    ----------
    label_data:
        Original label map loaded from the MICCAI *_glm.nii file or from a
        renamed label file.

    Returns
    -------
    np.ndarray
        Remapped label map with background = 0 and selected structures = 1..14.
    """
    remapped = np.zeros(label_data.shape, dtype=np.uint8)

    for original_label, new_label in LABEL_MAPPING.items():
        remapped[label_data == original_label] = new_label

    return remapped


def process_case(
    image_path: Path,
    label_path: Path,
    output_image_path: Path,
    output_label_path: Path,
) -> None:
    """
    Process one MICCAI case and save it in nnU-Net format.

    The T1 image is saved as:
        miccai_XXX_0000.nii.gz

    The remapped label map is saved as:
        miccai_XXX.nii.gz
    """
    image_nii = nib.load(str(image_path))
    label_nii = nib.load(str(label_path))

    image_data = image_nii.get_fdata()
    label_data = label_nii.get_fdata()

    remapped_labels = remap_labels(label_data)

    output_image_path.parent.mkdir(parents=True, exist_ok=True)
    output_label_path.parent.mkdir(parents=True, exist_ok=True)

    # Save image as float32 to reduce file size while preserving intensities.
    output_image = nib.Nifti1Image(
        image_data.astype(np.float32),
        affine=image_nii.affine,
        header=image_nii.header,
    )
    nib.save(output_image, str(output_image_path))

    # Save labels as uint8 because labels are integers from 0 to 14.
    # We use the image affine to keep labels aligned with the T1 image.
    output_label = nib.Nifti1Image(
        remapped_labels.astype(np.uint8),
        affine=image_nii.affine,
    )
    nib.save(output_label, str(output_label_path))


def main() -> None:
    """
    Convert selected MICCAI 2012 subcortical labels to nnU-Net-style files.

    Modify dataset_root to your local MICCAI 2012 dataset workspace.

    Expected input:
        imagesTr/miccai_001_t1.nii
        labelsTr/miccai_001.nii

    Output:
        imagesTr/miccai_001_0000.nii.gz
        labelsTr/miccai_001.nii.gz
    """
    dataset_root = Path("/path/to/2012_MICCAI_Challenge")

    images_dir = dataset_root / "imagesTr"
    labels_dir = dataset_root / "labelsTr"

    num_training_cases = 15

    for case_idx in range(1, num_training_cases + 1):
        case_id = f"miccai_{case_idx:03d}"

        print(f"Processing {case_id}")

        input_image_path = images_dir / f"{case_id}_t1.nii"
        input_label_path = labels_dir / f"{case_id}.nii"

        output_image_path = images_dir / f"{case_id}_0000.nii.gz"
        output_label_path = labels_dir / f"{case_id}.nii.gz"

        if not input_image_path.exists():
            raise FileNotFoundError(f"Missing image file: {input_image_path}")

        if not input_label_path.exists():
            raise FileNotFoundError(f"Missing label file: {input_label_path}")

        process_case(
            image_path=input_image_path,
            label_path=input_label_path,
            output_image_path=output_image_path,
            output_label_path=output_label_path,
        )

    print("Done.")


if __name__ == "__main__":
    main()