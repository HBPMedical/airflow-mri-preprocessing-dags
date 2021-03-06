"""Reorganise files in order to match the pre-processing pipelines requirements"""

from datetime import datetime, timedelta

from airflow import DAG

from common_steps import initial_step
from common_steps.check_local_free_space import check_local_free_space_cfg
from common_steps.prepare_pipeline import prepare_pipeline
from reorganisation_steps.cleanup_all_local import cleanup_all_local_cfg
from reorganisation_steps.copy_to_local import copy_to_local_cfg
from reorganisation_steps.reorganise import reorganise_cfg
from reorganisation_steps.trigger_ehr import trigger_ehr_pipeline_cfg
from reorganisation_steps.trigger_preprocessing import trigger_preprocessing_pipeline_cfg
from reorganisation_steps.trigger_metadata import trigger_metadata_pipeline_cfg


preparation_steps = ['copy_to_local']
reorganisation_steps = ['dicom_reorganise', 'nifti_reorganise']
finalisation_steps = ['trigger_preprocessing', 'trigger_metadata', 'trigger_ehr']

steps_with_file_outputs = preparation_steps + reorganisation_steps


def reorganise_files_dag(dataset, section, email_errors_to, max_active_runs,
                         reorganisation_pipelines=''):

    # Define the DAG

    dag_name = '%s_reorganise_files' % dataset.lower().replace(" ", "_")

    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime.now(),
        'retries': 1,
        'retry_delay': timedelta(seconds=120),
        'email': email_errors_to,
        'email_on_failure': True,
        'email_on_retry': True
    }

    dag = DAG(
        dag_id=dag_name,
        default_args=default_args,
        schedule_interval=None,
        max_active_runs=max_active_runs)

    upstream_step = check_local_free_space_cfg(dag, initial_step, section,
                                               map(lambda p: section + ':' + p, steps_with_file_outputs))

    upstream_step = prepare_pipeline(dag, upstream_step, True)

    if 'copy_to_local' in reorganisation_pipelines:
        upstream_step = copy_to_local_cfg(dag, upstream_step, section, section + ':copy_to_local')

    if 'dicom_reorganise' in reorganisation_pipelines:
        upstream_step = reorganise_cfg(dag, upstream_step, section, section + ':dicom_reorganise')
    elif 'nifti_reorganise' in reorganisation_pipelines:
        upstream_step = reorganise_cfg(dag, upstream_step, section, section + ':nifti_reorganise')

    # Cleanup step is used only to remove DICOM files or Nifti files copied locally.
    if 'copy_to_local' in reorganisation_pipelines:
        cleanup_step = cleanup_all_local_cfg(dag, upstream_step, section + ':copy_to_local')
        upstream_step.priority_weight = cleanup_step.priority_weight

    if 'trigger_preprocessing' in reorganisation_pipelines:
        trigger_preprocessing_pipeline_cfg(dag, upstream_step, dataset, section, section + ':trigger_preprocessing')
    # endif

    if 'trigger_metadata' in reorganisation_pipelines:
        trigger_metadata_pipeline_cfg(dag, upstream_step, dataset, section + ':trigger_metadata')
    # endif

    if 'trigger_ehr' in reorganisation_pipelines:
        trigger_ehr_pipeline_cfg(dag, upstream_step, dataset, section, section + ':trigger_ehr')
    # endif

    return dag
