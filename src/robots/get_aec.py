# python
import logging
import tempfile
import json

## storage
from src.storage import storage

## session
from src.fetch import session as sii_session

# utils
from src.utils import utils

## sns
from src.sns import snsTopic

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)

def download_aec(session, cookies, documento):
    """Get AEC from SII 

    Parameters:
        doc: dict = {
            'folio': xxx,
            'rut_deudor': xxxx,
            'tipo_documento': xxx,
            'rut_cliente': xxxx

        }

    Returns:
    """

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        rut_without_dv, rut_dv, _ = utils.format_rut(documento["rut_cliente"])
        payload = {
            "rut_emisor": rut_without_dv,
            "dv_emisor": rut_dv,
            "tipo_docto": documento['tipo_documento'],
            "folio": documento['folio'],
            "clave": "",
            "botonxml": "xml",
        }

        _result = session.post("https://palena.sii.cl/cgi_rtc/RTC/RTCDescargarXmlCons.cgi",headers=headers,data=payload,cookies=cookies)
        session.get('https://zeusr.sii.cl/cgi_AUT2000/autTermino.cgi')
        session.close()
        return save_file(documento=documento,data=_result)

    except Exception as err:
        print(f'ERROR: {err}')
        print(f"No fue posible descargar el AEC del folio {documento['folio']}")
        raise Exception(err)


def save_file(documento,data):
    logger.info("AEC  {} obtenido correctamente".format(documento["folio"]))
    filename = f'AEC_{documento["rut_cliente"].replace("-", "_")}_{str(documento["folio"])}_{documento["rut_deudor"].replace("-", "_")}.xml'
    
    try:
        tmp_file = tempfile.NamedTemporaryFile()
        tmp_file.write(data.text.encode('ISO-8859-1'))
        
        file_url = storage.save_to_s3(file=tmp_file.name,filename=filename)
        tmp_file.close()
        
        ## publish to topic
        message = {
            'rut_cliente': documento['rut_cliente'],
            'rut_deudor': documento['rut_deudor'],
            'folio': documento['folio'],
            'url_file': file_url,
            'event_type': 1
        }
        snsTopic.publish_event(message=json.dumps(message))
        
        return file_url
    except Exception as err:
        print(f"Ocurrió un error LINE 89: {err}")
    

def run(rut,password,documento):
    
    session, cookies = sii_session.login(rut=rut,password=password)
    logger.info(f'SESSION => {session}')
    
    logger.info('Obtener AEC')
    aec_file_url = download_aec(session=session,cookies=cookies,documento=documento)
    
    
    log = {
        **documento,
        'aec_file_url': aec_file_url,
    }

    print(f'get aec => {log}')
    
    return aec_file_url
