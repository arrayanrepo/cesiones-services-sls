## python
import datetime as dt
import logging

## save 
from src.storage import storage

## jinja
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)

def generate_pdf(data):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("/src/robots/certificado/template.html")
    now = dt.datetime.now()
    
    obj_data = {
        "folio": data["folio"],
        "parrafo": data["parrafo"],
        "array_final": data["array_final"],
        "nombre": "nombre",
        "rut_deudor": data["rut_deudor"],
        "fecha": data["fecha"],
        "fecha_sola": "fechasola",
        "folio_superior": data['folio_superior'],
        "fecha_certificado":  now.strftime("%d/%m/%Y %H:%M:%S")
    }


    filename = f'Certf_{data["rut_cliente"]}_{data["rut_deudor"]}_{data["folio"]}.pdf'
    content = template.render(obj_data)

    return storage.save_file(filename=filename,content=content)