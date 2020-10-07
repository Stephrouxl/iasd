from datetime import datetime, timedelta

#import airflow.hooks.S3_hook
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago

import pandas as pd

#from model import train_model

# the data was copied into my own S3 bucket
# set up some variables
#remote_bucket = 'iasd-klouvi-data'  # S3 bucket name where to store data and trained models
#data_path = 'petrol_consumption.csv'  # dataset file name
#trained_model_path = 'petrol_consumption_model.pickle'  # file where to save the trained model
#aws_credentials_key = 'aws_credentials'

args = {
    'owner': 'rouxel',  # the owner id
    'start_date': days_ago(0),
    'retry_delay': timedelta(seconds=10),
}

dag = DAG('petrol',
    default_args=args,
    schedule_interval="0 * * * *")


#def download_from_s3_task(output_path, **kwargs):
#    """
#        Download data from S3 bucket
#    """
    #hook = airflow.hooks.S3_hook.S3Hook(aws_credentials)  # AWS credentials are stored into Airflow connections manager
    #source_object = hook.get_key(key, bucket_name)
#    source_object.download_file(data_path)

def download():
    data = pd.read_csv('./iris.csv')


# let's start with a dummy task
start_task = DummyOperator(
    task_id='start_task',
    dag=dag,
)

# task to download the dataset from s3
download_data_task = PythonOperator(
    task_id='download_data_task',
    provide_context=True,
    python_callable=download,
    dag=dag,
)






