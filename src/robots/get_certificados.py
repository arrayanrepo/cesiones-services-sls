# python
import logging
import json

## session
from src.fetch import session as sii_session

## utils
from src.utils import utils

## sns
from src.sns import snsTopic

## certificados
from src.robots.certificado import certificado,parser_html,generate_pdf

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)


def run(rut,password, days, cesion):
    try:
        desde, hasta =  utils.get_dates(days=days,format_string='%d%m%Y')
        session, _ = sii_session.login(rut=rut,password=password)  
        
        table = certificado.consulta_individual(rut=rut,session=session, desde=desde, hasta=hasta, docto_certf=cesion)
        idx_check = parser_html.get_checked_certf_id(table=table, folio=cesion['folio'])
        certf_data = parser_html.get_data_certificado(checked=idx_check, session=session, desde=desde, hasta=hasta, docto_certf=cesion)
        file_url = generate_pdf.generate_pdf(data=certf_data)
        
        
        message = {
            'rut_cliente' : cesion['rut_cliente'],
            'rut_deudor': cesion['rut_deudor'],
            'folio': cesion['folio'],
            'url_file': file_url
        }
        
        snsTopic.publish_event(message=json.dumps(message))
        
        return {'statusCode': 200, 'file_url': file_url}
        
    except Exception as err:
        ## aqui volvemos a encolar la consulta en el queue
        print(err)
        return {'statusCode': 400, 'error': "error al obtener el certificado"}