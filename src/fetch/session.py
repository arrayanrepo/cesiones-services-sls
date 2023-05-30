## python
import logging

## utils
from src.utils import utils

## others
import requests


logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)


def login(password, rut):

    session = requests.Session()
    cookies = None

    logger.info("Inicio de sesion")
    headers2 = {"Content-Type": "application/json"}
    rut_without_dv, rut_dv, rut_format = utils.format_rut(rut)
    payload = {
        "rut": rut_without_dv,
        "dv": rut_dv,
        "referencia": "https://misiir.sii.cl/cgi_misii/siihome.cgi",
        "411": "",
        "rutcntr": rut_format,
        "clave": password,
    }

    try:
        logger.info("Inicio de sesion 1")
        init_sesion = session.post(
            "https://zeusr.sii.cl/cgi_AUT2000/CAutInicio.cgi",
            headers=headers2,
            data=payload,
        )
        print(f'SESSION => {init_sesion.text}')
        cookies = dict(init_sesion.cookies)
    except requests.exceptions.HTTPError as e:
        logger.info("No fue posible iniciar sesion")
        raise SystemExit(e)

    if cookies == {}:
        logger.info("no fue posible iniciar sesion, intentando nuevamente")
        try:
            logger.info("Re-Inicio de sesion ")
            init_sesion = session.post(
                "https://zeusr.sii.cl/cgi_AUT2000/CAutInicio.cgi",
                headers=headers2,
                data=payload,
            )
            print(f'SESSION 2 => {init_sesion.content}')
            cookies = dict(init_sesion.cookies)
        except requests.exceptions.HTTPError as e:
            logger.info("No fue posible iniciar sesion en reintento")
            raise SystemExit(e)

    if cookies == {}:
        raise SystemExit("No fue posible iniciar session ultimo intento")

    return (session, cookies)