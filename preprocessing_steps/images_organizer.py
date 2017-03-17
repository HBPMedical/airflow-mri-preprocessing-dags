"""

  Pre processing step: images organizer

  Configuration variables used:

  * :preprocessing section
    * INPUT_CONFIG
  * :preprocessing:dicom_organiser or :preprocessing:nifti_organiser section
    * LOCAL_FOLDER
    * DATA_STRUCTURE
    * DOCKER_IMAGE
    * DOCKER_INPUT_DIR
    * DOCKER_OUTPUT_DIR

"""


import re

from datetime import timedelta
from textwrap import dedent

from airflow import configuration
from airflow_pipeline.operators import DockerPipelineOperator

from common_steps import Step


def images_organizer_cfg(dag, upstream_step, preprocessing_section, step_section):
    dataset_config = configuration.get(preprocessing_section, 'INPUT_CONFIG')
    local_folder = configuration.get(step_section, 'LOCAL_FOLDER')
    data_structure = configuration.get(step_section, 'DATA_STRUCTURE')
    docker_image = configuration.get(step_section, 'DOCKER_IMAGE')
    docker_input_dir = configuration.get(step_section, 'DOCKER_INPUT_DIR')
    docker_output_dir = configuration.get(step_section, 'DOCKER_OUTPUT_DIR')

    m = re.search('.*:preprocessing:(.*)_organizer', step_section)
    dataset_type = m.group(1)

    return images_organizer(dag, upstream_step, dataset_config,
                            dataset_type=dataset_type,
                            data_structure=data_structure,
                            local_folder=local_folder,
                            docker_image=docker_image,
                            docker_input_dir=docker_input_dir,
                            docker_output_dir=docker_output_dir)


def images_organizer(dag, upstream_step,  dataset_config,
                     dataset_type, data_structure,
                     local_folder,
                     docker_image='hbpmip/hierarchizer:latest',
                     docker_input_dir='/input_folder',
                     docker_output_dir='/output_folder'):

    type_of_images_param = "--type " + dataset_type
    structure_param = "--attributes " + str(data_structure.split(':'))

    images_organizer_pipeline = DockerPipelineOperator(
        task_id='images_organizer_pipeline',
        output_folder_callable=lambda session_id, **kwargs: local_folder + '/' + session_id,
        pool='io_intensive',
        parent_task=upstream_step.task_id,
        priority_weight=upstream_step.priority_weight,
        execution_timeout=timedelta(hours=24),
        on_skip_trigger_dag_id='mri_notify_skipped_processing',
        on_failure_trigger_dag_id='mri_notify_failed_processing',
        dataset_config=dataset_config,
        dag=dag,
        image=docker_image,
        command=["--dataset {{ dag_run.conf['dataset'] }}", type_of_images_param, structure_param],
        container_input_dir=docker_input_dir,
        container_output_dir=docker_output_dir
    )

    if upstream_step.task:
        images_organizer_pipeline.set_upstream(upstream_step.task)

    images_organizer_pipeline.doc_md = dedent("""\
        # Images organizer pipeline

        Reorganise DICOM/NIFTI files to fit the structure expected by the following pipelines.

        Reorganised DICOM/NIFTI files are stored the the following locations:

        * Local folder: __%s__

        Depends on: __%s__
        """ % (local_folder, upstream_step.task_id))

    return Step(images_organizer_pipeline, 'images_organizer_pipeline', upstream_step.priority_weight + 10)
