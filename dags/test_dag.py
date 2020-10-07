import gzip
import logging
import re
from datetime import datetime, timedelta
from io import BytesIO
from xml.etree import ElementTree as ET

import requests
from airflow import DAG
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator


default_args = {
    'owner': 'ncrocfer',
    'start_date': datetime(2018, 10, 31),
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


logger = logging.getLogger(__name__)


NVD_MODIFIED_META_URL = 'https://static.nvd.nist.gov/feeds/xml/cve/2.0/nvdcve-2.0-Modified.meta'
NVD_MODIFIED_URL = 'https://static.nvd.nist.gov/feeds/xml/cve/nvdcve-2.0-Modified.xml.gz'
LAST_NVD_HASH = '/tmp/lastnvd'


def check_updates():
    logger.info("Downloading {url}...".format(url=NVD_MODIFIED_META_URL))

    resp = requests.get(NVD_MODIFIED_META_URL)
    buf = BytesIO(resp.content).read().decode('utf-8')

    nvd_sha256 = buf.split('sha256')[1][1:-2]
    logger.info("New NVD hash is : {hash}".format(hash=nvd_sha256))

    try:
        with open(LAST_NVD_HASH) as f:
            last_nvd256 = f.read()
    except FileNotFoundError:
        last_nvd256 = None
    logger.info("Local hash is : {hash}".format(hash=last_nvd256))

    if nvd_sha256 != last_nvd256:
        logger.info("Hashes differ, Saucs database needs to be updated...")
        return {'updated': True, 'hash': nvd_sha256}
    else:
        logger.info("Hashes are the same, nothing to do.")
        return {'updated': False}


def download_xml(ds, **context):
    update = context['task_instance'].xcom_pull(task_ids='CheckUpdates')
    if not update['updated']:
        return

    logger.info("Downloading {url}...".format(url=NVD_MODIFIED_URL))

    resp = requests.get(NVD_MODIFIED_URL)
    buf = BytesIO(resp.content)
    data = gzip.GzipFile(fileobj=buf)

    xml_string = data.read().decode('utf-8')
    xml_string = re.sub(' xmlns="[^"]+"', '', xml_string)

    with open('/tmp/{0}.xml'.format(ds), 'w') as f:
        f.write(xml_string)


def parse_xml(ds, **context):
    update = context['task_instance'].xcom_pull(task_ids='CheckUpdates')
    if not update['updated']:
        return

    parser = ET.XMLParser(encoding="utf-8")
    tree = ET.parse('/tmp/{0}.xml'.format(ds), parser=parser)
    root = tree.getroot()

    for child in root:
        logger.info("Parsing {cve}...".format(cve=child.attrib.get('id')))

        # 1. Process the CVE (new CVE, CPE updated, references updated, CVSS updated...)
        # 2. Create an alert for all impacted users


def send_mails(ds, **context):
    update = context['task_instance'].xcom_pull(task_ids='CheckUpdates')
    if not update['updated']:
        return

    logger.info('Sending mail for users with an alert')
    """users = get_users_with_alerts()

    for user in users:
        send_user_mail()
        user.new_alerts = False"""

    # We're done, we can set the new NVD hash in local
    with open(LAST_NVD_HASH, 'w') as f:
        f.write(update['hash'])


dag = DAG('demo', default_args=default_args, schedule_interval='0 * * * *')

with dag:
    check_updates_op = PythonOperator(
        task_id='CheckUpdates',
        python_callable=check_updates
    )

    download_xml_op = PythonOperator(
        task_id='DownloadXml',
        provide_context=True,
        python_callable=download_xml
    )

    parse_xml_op = PythonOperator(
        task_id='ParseXml',
        provide_context=True,
        python_callable=parse_xml
    )

    send_mails_op = PythonOperator(
        task_id='SendMails',
        provide_context=True,
        python_callable=send_mails
    )


# Order the tasks
check_updates_op >> download_xml_op >> parse_xml_op >> send_mails_op

"""
# Can be written :
check_updates_op.set_downstream(download_xml_op)
download_xml_op.set_downstream(parse_xml_op)
parse_xml_op.set_downstream(send_mails_op)
"""
