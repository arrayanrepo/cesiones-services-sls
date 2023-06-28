## python 
import datetime as dt
import time
import logging
import pytz

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)

global timezone
timezone = pytz.timezone('America/Santiago')


FORMAT = '%d%m%Y'

def retry_fetch(func, retries=5):

    def retry_wrapper(*args, **kwargs):

        attemps = 0
        while attemps < retries:
            logger.info('Reintentado get certificado')
            print('Intento numero {}'.format(attemps))
            resp = func(*args, **kwargs)
            if resp.status_code == 200:
                return resp
            else:
                logger.info('Reobtener certificado')
                print('Intento numero {}'.format(attemps))
                time.sleep(1)
                attemps += 1

    return retry_wrapper


def format_number(value):
    _value = round(float(value))
    _format = '{:,}'.format(_value).replace(',','.')
    return f'$ {_format}'


def format_rut( rut):

    rut_aux = rut.split("-")
    rr = rut_aux[0]
    dvr = rut_aux[1]

    _rut_without_divisor = rr
    _divisor_rut = dvr

    # Se formatea el rut para que quede XX.XXX.XXX-X
    rutFormat = "{0:,}".format(int(rr))
    rutFormat = str(rutFormat).replace(",", ".")
    _rut_format = rutFormat + "-" + dvr

    return _rut_without_divisor, _divisor_rut, _rut_format

def get_dates(days, format_string = FORMAT):

    now = dt.datetime.now(timezone)
    _init_date = now - dt.timedelta(days=int(days))

    desde = _init_date.strftime(format_string)
    hasta = now.strftime(format_string)
    return (desde, hasta)

def get_today():
    
    now = dt.datetime.now(timezone)
    return now


def format_string_date(date, format_input, format_output):
    
    if date is None:
        return None
    
    object_date = dt.datetime.strptime(date, format_input)
    output_date = object_date.strftime(format_output)
    return output_date


def format_date(date : dt.datetime, datestring_format : str) -> str:
    
    if date is None:
        return None
    
    _date = date.strftime(datestring_format)
    return _date