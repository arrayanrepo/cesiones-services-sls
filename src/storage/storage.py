## python
import logging
import os
import tempfile
import subprocess

## jinja
from jinja2 import Environment, FileSystemLoader

## utils
from src.utils import utils

## boto3
import boto3

## requests
import requests

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)

BUCKET_NAME = os.environ.get('BUCKET_NAME')
SUBDIR = os.environ.get('SUBDIR')

def download_s3_file(url):
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.content
    
    except Exception as err:
        print(f'Error downloading s3 file {err}')
        return False
    

def save_to_s3(file,filename):
    now = utils.get_today().strftime('%d_%m_%Y')

    try:
        s3 = boto3.client('s3')
        # Sube el archivo al bucket de S3
        result = s3.upload_file(file, BUCKET_NAME, f'{SUBDIR}/{now}/{filename}')
        print(f' UPLOADING FILE => {result}')
        # Genera la URL del archivo cargado
        url_file = f"https://{BUCKET_NAME}.s3.amazonaws.com/{SUBDIR}/{now}/{filename}"
        return url_file
    
    except Exception as err:
        logger.error(f"Ocurrió un error al subir el archivo a S3: {err}")
        raise Exception("No se puede subir el archivo")


def save_file(content,filename):    
    try:
        tmp_file = tempfile.NamedTemporaryFile(suffix='.html')
        tmp_file.write(content.encode('utf-8'))
        tmp_file.flush()
        command = f'wkhtmltopdf --load-error-handling ignore {tmp_file.name} {tmp_file.name.replace(".html",".pdf")}'
        subprocess.run(command, shell=True)     
        file_url = save_to_s3(file=tmp_file.name.replace('.html','.pdf'),filename=filename)
        tmp_file.close()
        
        return file_url
    
    except Exception as err:
        logger.error(f"Ocurrió un error: {err}")

def generate_pdf(data,filename,template):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template)
    content = template.render(data)
    return save_file(filename=filename,content=content)