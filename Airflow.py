# import the libraries
from datetime import timedelta
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators
from airflow.operators.bash_operator import BashOperator
# This makes scheduling easy
from airflow.utils.dates import days_ago

#Define DAG arguments
default_args={
    'owner':'Kiryu Sento',
    'start_date': days_ago(0),
    'email':['Build@sysmail.com'],
    'email_on_failure':True,
    'email_on_retry': True,
    'retries':1,
    'retry_delay':timedelta(minutes=5),
}

#Define the DAG
dag=DAG(
    dag_id='ETL_toll_data',
    default_args=default_args,
    description='Apache Airflow Final Assignment',
    schedule_interval=timedelta(days=1),   
)

#Create a task to unzip data
unzip_data=BashOperator(
    task_id='unzip_data',
    bash_command='tar -xvzf /home/project/airflow/dags/finalassignment/tolldata.tgz -C /home/project/airflow/dags/finalassignment/staging',
    dag=dag,
)
#Create a task to extract data from csv file
extract_data_from_csv=BashOperator(
    task_id="extract_data_from_csv",
    bash_command='cut -f1-4 -d","  /home/project/airflow/dags/finalassignment/staging/vehicle-data.csv > /home/project/airflow/dags/finalassignment/staging/csv_data.csv',
    dag=dag,
)
# Create a task to extract data from tsv file

extract_data_from_tsv = BashOperator(
    task_id='extract_data_from_tsv',
    bash_command='cut -f3,5,6 /home/project/airflow/dags/finalassignment/staging/tollplaza-data.tsv >/home/project/airflow/dags/finalassignment/staging/tsv_data.csv',
    dag=dag,
)
# Create a task to extract data from fixed width file

extract_data_from_fixed_width = BashOperator(
    task_id='extract_data_from_fixed_width',
    bash_command='tr -s ' ' < /home/project/airflow/dags/finalassignment/staging/payment-data.txt | cut -d" " -f11-12 > /home/project/airflow/dags/finalassignment/staging/fixed_width_data.csv',
    dag=dag,
)
# Create a task to consolidate data extracted from previous tasks

consolidate_data = BashOperator(
    task_id='consolidate_data',
    bash_command='paste /home/project/airflow/dags/finalassignment/staging/csv_data.csv /home/project/airflow/dags/finalassignment/staging/tsv_data.csv /home/project/airflow/dags/finalassignment/staging/fixed_width_data.csv > /home/project/airflow/dags/finalassignment/staging/extracted_data.csv',
    dag=dag,
)
# define the task 'transform'

transform_data = BashOperator(
    task_id='transform_data',
    bash_command='tr "[a-z]" "[A-Z]" < /home/project/airflow/dags/finalassignment/staging/extracted_data.csv > /home/project/airflow/dags/finalassignment/staging/transformed_data.csv',
    dag=dag,
)
# task pipeline
unzip_data >> extract_data_from_csv >> extract_data_from_tsv >> extract_data_from_fixed_width >> consolidate_data >> transform_data
