## python
import logging
import datetime as dt
import os
import tempfile
import subprocess

## boto3
import boto3


logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)

BUCKET_NAME = os.environ.get('BUCKET_NAME')
SUBDIR = os.environ.get('SUB_DIR')

def save_to_s3(file,filename):
    now = dt.datetime.now().strftime('%d_%m_%Y')
    try:
        s3 = boto3.client('s3')
        # Sube el archivo al bucket de S3
        s3.upload_file(file, BUCKET_NAME, f'{SUBDIR}/{now}/{filename}')
        # Genera la URL del archivo cargado
        url_file = f"https://{BUCKET_NAME}.s3.amazonaws.com/{SUBDIR}/{now}/{filename}"
        logger.info(f'URL file {url_file}')
        
        return url_file
    
    except Exception as e:
        logger.error("Ocurrió un error al subir el archivo a S3:", str(e))
        raise Exception("No se puede subir el archivo")
        

def save_file(content,filename):    
    try:
        tmp_file = tempfile.NamedTemporaryFile(suffix='.html')
        tmp_file.write(content.encode('utf-8'))
        tmp_file.flush()
        command = f'wkhtmltopdf  --load-error-handling ignore {tmp_file.name} {tmp_file.name.replace(".html",".pdf")}'
        subprocess.run(command, shell=True)     
        file_url = save_to_s3(file=tmp_file.name.replace('.html','.pdf'),filename=filename)
        tmp_file.close()
        
        return file_url
    except Exception as e:
        logger.error("Ocurrió un error:", str(e))
