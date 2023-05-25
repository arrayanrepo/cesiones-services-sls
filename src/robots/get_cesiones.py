# python
import logging
import json

## session
from src.fetch import session as sii_session

## database
from src.database import querys

## sns
from src.sns import snsTopic

## utils
from src.utils import utils

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)



def fetch_get_cesiones(session,cookies,tipo_consulta, desde, hasta):
    
    """
        Util de scraping de cesiones dada una empresa y un tiempo determinado, ademas podemos sacar 
        tanto las cesiones a la empresa como la cesiones de la empresa
        
        
        tipo_consulta 2 = cesiones realizadas
        tipo_consulta 1 = cesiones hechas a terceros
    """
    
    url = 'https://palena.sii.cl/cgi_rtc/RTC/RTCConsultaCesiones.cgi'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    payload = {
        'TIPOCONSULTA': tipo_consulta,
        'TXTXML': 'TXT',
        'DESDE': desde,
        'HASTA': hasta,
    }
    logger.info(f'Request para obtener cesiones de la fecha {desde} hasta {hasta}')
    try:
        response = session.post(url, headers=headers, data=payload, cookies=cookies)
        logger.info("Cesiones obtenidas")
        return response.text
    except Exception as err:
        logger.info("No fue posible obtener las cesiones")
        raise SystemError(f"No fue posible obtener las cesiones {err}")


def clean_cesiones(data):
    
    cesiones = []
    
    logger.info('clean data')
    logger.info(f'TOTAL CESIONES => {len(data.splitlines())}')
    for line in data.splitlines():
        info = line.split(';')
        if len(info) == 18:
            
            if info[0] != 'VENDEDOR':
                obj = {
                    'rut_cliente': info[0],
                    'estado_cesion': info[1],
                    'rut_deudor': info[2],
                    'mail_deudor': info[3],
                    'tipo_documento': info[4],
                    'nombre_doc': info[5],
                    'folio': info[6],
                    'fch_emis_dte': info[7],
                    'mnt_total': info[8],
                    'cedente': info[9],
                    'rz_cedente': info[10],
                    'mail_cedente': info[11],
                    'cesionario': info[12],
                    'rz_cesionario': info[13],
                    'mail_cesionario': info[14],
                    'fch_cesion': info[15],
                    'mnt_cesion': info[16],
                    'fch_vencimiento': info[17]
                }
                
                ## validacion de que ya exista la cesion
                results = querys.validate_records(rut_cliente=obj['rut_cliente'],rut_deudor=obj['rut_deudor'],folio=obj['folio'])
                
                if len(results) > 0:
                    if all(results[0].values()):
                        return cesiones
                    else:
                        snsTopic.publish_event(message=json.dumps(obj))
                        cesiones.append(obj)
                else:
                    snsTopic.publish_event(message=json.dumps(obj))
                    cesiones.append(obj)
                
            else:    
                continue
    return cesiones

def run(rut ,password ,days , tipo_consulta):
    
    desde, hasta = utils.get_dates(days=days, format_string='%d%m%Y')
    session, cookies = sii_session.login(rut=rut,password=password)        
    
    fetched_cesiones = None
    logger.info('Obtener cesiones')
    cesiones = fetch_get_cesiones(session=session ,cookies=cookies, tipo_consulta=tipo_consulta, desde=desde, hasta=hasta)
    
    if cesiones:
        fetched_cesiones = clean_cesiones(data=cesiones)
    
    return fetched_cesiones
    
