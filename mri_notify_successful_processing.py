"""

Inform administrators when processing on a MRI session has been skipped because of missing / incorrect data

"""

import logging
import os

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators import SlackAPIPostOperator
from airflow import configuration

from util import dicom_import
from util import nifti_import


# constants

DAG_NAME = 'mri_notify_successful_processing'

slack_token = str(configuration.get('mri', 'SLACK_TOKEN'))
slack_channel = str(configuration.get('mri', 'SLACK_CHANNEL'))
slack_channel_user = str(configuration.get('mri', 'SLACK_CHANNEL_USER'))

# Define the DAG

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'retries': 1,
    'retry_delay': timedelta(seconds=120),
    'email': None,
    'email_on_failure': False,
    'email_on_retry': False
}

dag = DAG(
    dag_id=DAG_NAME,
    default_args=default_args,
    schedule_interval=None)

post_on_slack = SlackAPIPostOperator(
    task_id='post_on_slack',
    token=slack_token,
    channel=slack_channel,
    username=slack_channel_user,
    text=':white_check_mark: Processed scan session *{{ dag_run.conf["session_id"] }}* performed on {{ dag_run.conf["scan_date"] | default("?") }} for participant {{ dag_run.conf["participant_id"] | default("?") }}',
    icon_url='https://raw.githubusercontent.com/airbnb/airflow/master/airflow/www/static/pin_100.png',
    dag=dag
)

post_on_slack.doc_md = """\
# Post information about the processed MRI scan session on Slack

Post information about the processed MRI scan session on Slack channel %s
""" % slack_channel
