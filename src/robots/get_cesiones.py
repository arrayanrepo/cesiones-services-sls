# python
import logging
import json
import xml.etree.ElementTree as ET

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
        'TXTXML': 'XML',
        'DESDE': desde,
        'HASTA': hasta,
    }
    logger.info(f'Request para obtener cesiones de la fecha {desde} hasta {hasta}')
    try:
        response = session.post(url, headers=headers, data=payload, cookies=cookies)
        logger.info("Cesiones obtenidas")
        session.close()
        session.get('https://zeusr.sii.cl/cgi_AUT2000/autTermino.cgi')
        return response.content
    except Exception as err:
        logger.info("No fue posible obtener las cesiones")
        raise SystemError(f"No fue posible obtener las cesiones {err}")


def clean_cesiones(data):
    decode_data = data.decode("utf-8")
    root = ET.fromstring(decode_data)
    sesiones = root.findall(".//CESION")
    cesiones = []

    for sesion in sesiones:
        
        obj = {
            "rut_cliente": sesion.find("VENDEDOR").text,
            "estado_cesion": sesion.find("ESTADO_CESION").text,
            "rut_deudor": sesion.find("DEUDOR").text,
            "mail_deudor": sesion.find("MAIL_DEUDOR").text,
            "tipo_documento": sesion.find("TIPO_DOC").text,
            "nombre_doc": sesion.find("NOMBRE_DOC").text,
            "folio": sesion.find("FOLIO_DOC").text,
            "fch_emis_dte": sesion.find("FCH_EMIS_DTE").text,
            "mnt_total": sesion.find("MNT_TOTAL").text,
            "cedente": sesion.find("CEDENTE").text,
            "rz_cedente": sesion.find("RZ_CEDENTE").text,
            "mail_cedente": sesion.find("MAIL_CEDENTE").text,
            "cesionario": sesion.find("CESIONARIO").text,
            "rz_cesionario": sesion.find("RZ_CESIONARIO").text,
            "mail_cesionario": sesion.find("MAIL_CESIONARIO").text,
            "fch_cesion": sesion.find("FCH_CESION").text,
            "mnt_cesion": sesion.find("MNT_CESION").text,
            "fch_vencimiento": sesion.find("FCH_VENCIMIENTO").text,
        }
        
        
        results = querys.validate_records(rut_cliente=obj['rut_cliente'],rut_deudor=obj['rut_deudor'],folio=obj['folio'])
        
        if results and  len(results) > 0:
            if not all(results[0].values()):
                snsTopic.publish_event(message=json.dumps(obj))
                print(f'Message => {obj}')
                cesiones.append(obj)
        else:
            snsTopic.publish_event(message=json.dumps(obj))
            cesiones.append(obj)
    
    return cesiones   
    
def run(rut ,password ,days , tipo_consulta):
    
    desde, hasta = utils.get_dates(days=days, format_string='%d%m%Y')
    session, cookies = sii_session.login(rut=rut,password=password)        
    
    fetched_cesiones = []
    logger.info('Obtener cesiones')
    cesiones = fetch_get_cesiones(session=session ,cookies=cookies, tipo_consulta=tipo_consulta, desde=desde, hasta=hasta)
    
    if cesiones:
        fetched_cesiones = clean_cesiones(data=cesiones)
    
    return fetched_cesiones
    
