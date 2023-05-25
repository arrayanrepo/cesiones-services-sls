## python
import logging
import datetime as dt


## utils
from src.utils import utils

## others
import requests
import bs4
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)


@utils.retry_fetch
def fetch_certificado(payload, session):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    logger.info('Retry fetch certificado')
    get_certificado = session.post(url='https://palena.sii.cl/cgi_rtc/RTC/RTCCertMas.cgi', data=payload, headers=headers)
    return get_certificado

def get_checked_certf_id(table,folio):
    indice = None
    index = 0
    valor = 0

    for row in table.findAll('th'):
        if row.string == 'Folio':
            indice = index

        index += 1
    tr = table.findAll('tr')
    checked = None
    for col in range(1, len(tr)):
        row = tr[col].findAll('td')
        # para la solicitud del certificado no pide un valor chk que se encuentra en el input de tipo checkbox
        # referencia inspecionar el elemeneto en el navegador para localizar el valor
        # <input type="checkbox" name="chk" value="31306538" >
        if int(row[indice].string) == folio:
            checked = row[valor].input['value']
            break
    logger.info(f'Checked certf => {checked}')
    return checked



def get_data_certificado(checked, session,desde,hasta,docto_certf):
    # Hacemos de nuevo un post a la url https://palena.sii.cl/cgi_rtc/RTC/RTCCertMas.cgi para obtener el certifiado
    # este certificado viene en formato HTML es necesario parsear para construir de nuevo el certificado
    try:

        payload = {
            'chk': checked,
            'STEP': '2',
            'TIPOCERT': '3',
            'TIPOCONSULTA': '2',
            'RUT1': docto_certf['rut_cliente'],
            'RUT2': docto_certf['rut_deudor'],
            'DESDE': desde,
            'HASTA': hasta
        }

        ## fecth del certificado
        get_certificado = fetch_certificado(payload=payload, session=session)
        if (get_certificado.status_code == 200 and hasattr(get_certificado, "text")):
            return clean_response(data=get_certificado,folio=docto_certf['folio'],rut_deudor=docto_certf['rut_deudor'],rut_cliente=docto_certf['rut_cliente'],desde=desde)
        else:
            raise SystemError("Error al limpiar la data")

    except requests.exceptions.HTTPError as err:
        logger.info(f'No fue posible obtener el certificado => {err}')
        raise SystemExit(err)



def clean_response(data,folio,rut_deudor,rut_cliente,desde):
    soup = BeautifulSoup(data.text, 'html.parser')
    parrafoRaw = soup.find_all("p")

    # podriamos tener status_code == 200 pero el servidor puede darnos un texto de que no se encuentra disponible
    # levantamos una excepcion para evitar que el script se rompa
    parrafo = None
    rows = None
    try:
        parrafo = parrafoRaw[0].get_text()
        table = soup.find_all('table')
        rows = table[2].find_all('tr')

        foliosuperior = soup.find_all("b")[0]
        folio_prncipal = foliosuperior.get_text()
        
    except bs4.FeatureNotFound as err:
        logger.info('No fue posible acceder a los certificados')
        raise SystemExit(str(err))

    except IndexError as err:
        logger.error(err)
        raise SystemExit(err)

    index = 0
    obj = {}
    last_list = []
    for row in rows:
        if index > 1:

            cols = row.find_all('td')
            monto = cols[4].find('script', type='text/javascript').text.split("'")
            monto_credito = cols[7].find('script', type='text/javascript').text.split("'")

            obj = {
                "rut": cols[0].text,
                "tipo_documento": cols[1].text,
                "numero_folio": cols[2].text,
                "fecha": cols[3].text,
                "monto": utils.format_number(int(monto[1])) if monto[1] != None else None,
                "fecha_inicio": cols[5].text,
                "fecha_vecimiento": cols[6].text,
                "monto_credito": utils.format_number(int(monto_credito[1])) if monto_credito[1] != None else None
            }

            last_list.append(obj)
        index += 1

    if len(last_list) > 0:
        FORMAT = "%d%m%Y%H%M%S"
        certificado_data = {
            "archivo": f"CMM_{rut_cliente}_{rut_deudor}_{folio}_{dt.datetime.now().strftime(FORMAT)}.pdf",
            'array_final': last_list,
            "folio": folio,
            "fecha": desde,
            "parrafo": parrafo,
            "rut_deudor": rut_deudor,
            "rut_cliente": rut_cliente,
            "docto": folio,
            "folio_superior": folio_prncipal
        }
        logger.info('Retornando objeto de certificado')
        return certificado_data
