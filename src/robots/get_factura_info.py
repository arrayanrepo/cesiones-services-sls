
## python
import logging
import json

## dte
from src.dte import dte_parser

## storages
from src.storage import storage

## sns
from src.sns import snsTopic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run(data):

    content = storage.download_s3_file(data['url_file'])
    
    if not content:
        return False
    
    try:
        data_parser = dte_parser.parser_dte(content=content)
        
        factura = data_parser['factura']
        cliente = data_parser['emisor']
        deudor = data_parser['receptor']
            
        filename = f"factura_{factura['folio']}_{cliente['rut_emisor']}_{deudor['rut_receptor']}_.pdf" 
        
        url = storage.generate_pdf(data=data_parser,filename=filename,template='/src/dte/invoice.html')
        
        message = {
        'rut_cliente': data['rut_cliente'],
        'rut_deudor': data['rut_deudor'],
        'folio': data['folio'],
        'url_file': data['url_file'],
        }
        
        snsTopic.publish_event(message=json.dumps(message))
        
        return url 
    
    except Exception as err:
        print(f'ERROR creating PDF {err}')
        return False