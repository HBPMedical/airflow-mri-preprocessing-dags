[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/LREN-CHUV/airflow-mri-preprocessing-dags/blob/master/LICENSE) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/8c5c9dc3cfb8492f870369c973f3cc8c)](https://www.codacy.com/app/hbp-mip/airflow-mri-preprocessing-dags?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=LREN-CHUV/airflow-mri-preprocessing-dags&amp;utm_campaign=Badge_Grade)

# Airflow MRI preprocessing DAGs

Requirements:

* airflow-imaging-plugins
* mri-preprocessing-pipeline

TODO: it should use mri-meta-extract

## Setup and configuration

### Airflow setup for MRI scans pipeline:

* Create the following pools:
   * image_preprocessing with N slots, where N is less than the number of vCPUs available on the machine

* In Airflow config file, add the [mri] section with the following entries:
   * PIPELINES_PATH: path to the root folder containing the Matlab scripts for the pipelines
   * PROTOCOLS_FILE: path to the MRI acquisition protocol file
   * DICOM_LOCAL_FOLDER: path containing the anonimised DICOM files coming from the MRI scanner and already anonimised by a tool
   * NIFTI_LOCAL_FOLDER: path for the image files converted to Nifti
   * NIFTI_SERVER_FOLDER: long term storage location for the image files converted to Nifti
   * NEURO_MORPHOMETRIC_ATLAS_LOCAL_FOLDER: path for the results of neuro morphometric atlas pipeline
   * NEURO_MORPHOMETRIC_ATLAS_SERVER_FOLDER: long term storage location for the results of neuro morphometric atlas pipeline
   * MPM_MAPS_LOCAL_FOLDER: path for the results of MPM maps pipeline
   * MPM_MAPS_SERVER_FOLDER: for the results of MPM maps pipeline
