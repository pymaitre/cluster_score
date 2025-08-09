# CAC Score Extractor

This script extracts and processes Coronary Artery Calcium (CAC) scores from DICOM RTSTRUCT files. It outputs an Excel summary of patient IDs, ROI names, CAC scores, and related metadata.

## install dependencies
A pyproject.toml is present.
Create a python venv using a python version >=3.10.
Execute the command `pip install -e .`.

## testing notebook

An IBSI test patient is included inside the test folder, with GTV as the only ROI available.

## Directory Structure

- DICOM RTSTRUCT files must be stored in patient-specific folders inside the `directory_dcm`.
- Results are saved to `directory_out`.

## Folder Structure

Your input directory (`directory_dcm`) must follow this structure:

```
directory_dcm/
├── 1234567/
│   └── CT/
│       └── CT_i/
│           ├── CT/           # Contains CT DICOM files
│           └── RTst/         # Contains RTSTRUCT DICOM files
├── 9876543/
│   └── CT/
│       └── CT_i/
│           ├── CT/
│           └── RTst/
└── ...
```

## Configuration

All configuration parameters are stored in `conf_CAC_score.yml`.

Example:
```yaml
directory_dcm: '/path/to/input/DICOMs'
directory_out: '/path/to/output/results'
patient_ids: ['1234567', '9876543']
roi_name_prefix: 'CAC_'  #define the name of the ROI as is written in rtstruct file
rtstruct_name_pattern: 'RTSTRUCT.dcm' #choose a common rtstruct name pattern
threshold : 129 #choose a threshold over which pixel values will be included in the cluster exploration
