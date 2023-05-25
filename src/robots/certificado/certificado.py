# python
import logging


# others
import requests
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)


def consulta_individual(session, desde, hasta, docto_certf, rut):
    """
        Metodo para consultar cesiones individuales
        args :

            rut_cliente     : string
            rut_deudor      : string
            folio           : string
            tipo_documento  : string
    """
    logger.info(f"Consulta de la cesion del cliente {docto_certf['rut_cliente']} y el deudor {docto_certf['rut_deudor']}")

    payload = {
        'STEP': 1,
        'RUTQ': rut,
        'TIPOCONSULTA': 2,
        'DESDE': desde,
        'HASTA': hasta,
        'RUT1':  docto_certf['rut_cliente'],
        'RUT2':  docto_certf['rut_deudor'],
    }

    # intentamos acceder a la pagina de certificados de session del SII
    # "https://palena.sii.cl/cgi_rtc/RTC/RTCCertMas.cgi"
    # filtramos por rut_cliente y rut deudor  y las fechas para obtener los certificados disponibles
    logger.info('wait for 2 seconds')
    try:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = session.post(url='https://palena.sii.cl/cgi_rtc/RTC/RTCCertMas.cgi', data=payload, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        index = 0
        table = None
        for row in soup.findAll("table", {"cellpadding": "3"}):
            if row != 0:
                table = row
            index = index + 1

        # parseamos la tabla que nos devuelve la interfaz
        # para luego verificar si el folio que estamos buscar se encuentra visible
        if table != None:
            total_rows = len(table.find('tbody').find_all('tr'))
            
            if total_rows > 0:
                return table
            else:
                return SystemExit("No existe el certificado")
        
        else:
            logger.info('la consulta no pudo realizarse')
            return Exception(f'fue posible obtener el certificado')

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as err:
        raise Exception(f'No fue posible hacer la consulta => ERROR: {err}')
