## python
from xml.dom import minidom
import base64
import tempfile
from typing import Dict
import logging

## utils
from src.utils import utils


## barcode
from pdf417 import encode, render_svg


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_base64(filepath):
    encode_file = None
    with open(filepath, 'rb') as file:
        encode_file = base64.b64encode(file.read()).decode('utf-8')
    return encode_file 

def get_tag(content, tag):
    
    if len(content.getElementsByTagName(tag)) == 0:
        return None
    return content.getElementsByTagName(tag)[0].firstChild.data
    
    
def asignar_tipo_dte_palabras(number_type : int) -> Dict[str,str]:
    number_type_palabras = None
    number_type_abreviatura = None
    
    if number_type == 33:
        number_type_palabras = "FACTURA ELECTRÓNICA"
        number_type_abreviatura = "FC"
    elif number_type == 34:
        number_type_palabras = "ELECTRÓNICA EXENTA"
        number_type_abreviatura = "FC"
    elif number_type == 30:
        number_type_palabras = "AFECTA"
        number_type_abreviatura = "FC"
    elif number_type == 43:
        number_type_palabras = "Liquidación-Factura Electrónica"
        number_type_abreviatura = "LFE"
    elif number_type == 46:
        number_type_palabras = "FACTURA DE COMPRA ELECTRÓNICA"
        number_type_abreviatura = "FCI"  # Factura de compra Interna
    elif number_type == 52:
        number_type_palabras = "GUÍA DE DESPACHO ELECTRÓNICA"
        number_type_abreviatura = "GD"
    elif number_type == 56:
        number_type_palabras = "NOTA DE DÉBITO ELECTRÓNICA"
        number_type_abreviatura = "ND"
    elif number_type == 61:
        number_type_palabras = "NOTA DE CRÉDITO ELECTRÓNICA"
        number_type_abreviatura = "NC"
    elif number_type == 110:
        number_type_palabras = "Factura de Exportación"
        number_type_abreviatura = "FEXP"
    elif number_type == 111:
        number_type_palabras = "Nota de Débito de Exportación"
        number_type_abreviatura = "NDE"
    elif number_type == 112:
        number_type_palabras = "Nota de Crédito de Exportación"
        number_type_abreviatura = "NCE"

    return {
        'number_type_palabras': number_type_palabras,
        'number_type_abreviatura': number_type_abreviatura
    }

def parser_dte(content):
        
    doc = minidom.parseString(content)
    # Obtener los elementos principales
    encabezado = doc.getElementsByTagName("Encabezado")[0]

    ## datos factura
    id_doc = encabezado.getElementsByTagName("IdDoc")[0]
    
    
    tipo_dte = get_tag(id_doc,"TipoDTE")
    folio = get_tag(id_doc,"Folio")
    fecha_emision = utils.format_string_date(get_tag(id_doc,"FchEmis"),'%Y-%m-%d', '%d/%m/%Y')
    fma_pago = get_tag(id_doc,"FmaPago")

    
    ## cliente
    emisor = encabezado.getElementsByTagName("Emisor")[0]

    rut_emisor = get_tag(emisor,'RUTEmisor')
    razon_social_emisor = get_tag(emisor,'RznSoc')
    giro_emisor = get_tag(emisor,'GiroEmis')
    dir_emisor = get_tag(emisor,'DirOrigen')
    cmna_emisor = get_tag(emisor,'CmnaOrigen')
    ciudad_emisor = get_tag(emisor,'CiudadOrigen')

    ## deudor
    receptor = encabezado.getElementsByTagName("Receptor")[0]
    rut_receptor = get_tag(receptor,'RUTRecep')
    razon_social_receptor = get_tag(receptor,'RznSocRecep')
    giro_receptor = get_tag(receptor,'GiroRecep')
    dir_receptor = get_tag(receptor,'DirRecep')
    cmna_receptor = get_tag(receptor,'CmnaRecep')
    ciudad_receptor = get_tag(receptor,'CiudadRecep')
    
    ## totales
    totales = encabezado.getElementsByTagName("Totales")[0]

    neto = get_tag(totales,'MntNeto')
    tasa_iva = get_tag(totales,'TasaIVA')
    iva = get_tag(totales,'IVA')
    total = get_tag(totales,'MntTotal')
    
    # Extraer datos del Detalle
    
    detalle = doc.getElementsByTagName('Detalle')
    detalles = []
    for detalle_item in detalle:
        nro_lin_det = get_tag(detalle_item, 'NroLinDet')
                
        nmb_item = get_tag(detalle_item, 'NmbItem')
        dsc_item = get_tag(detalle_item, 'DscItem')
        qty_item = get_tag(detalle_item, 'QtyItem')
        prc_item = get_tag(detalle_item, 'PrcItem')
        monto_item = get_tag(detalle_item, 'MontoItem')
        

        detalle_data = {
            "NroLinDet":  str(nro_lin_det).lower(),
            "NmbItem":  str(nmb_item).lower(),
            "DscItem":  str(dsc_item).lower(),
            "QtyItem":  str(qty_item).lower(),
            "PrcItem":  utils.format_number(prc_item),
            "MontoItem": utils.format_number(monto_item),
        }
        detalles.append(detalle_data)
    
    path = generate_pdf417_barcode(string_timbre=doc.getElementsByTagName('TED')[0].toxml())
    
    data = {
        'factura': {
            'tipo_dte': asignar_tipo_dte_palabras(number_type=int(tipo_dte)),
            'folio': folio,
            'fecha_emision': fecha_emision,
            'fma_pago': fma_pago,
            'mnt_pagos': 0,
            'monto_pago': 0,
            'fecha_pago': 0,
            'term_pago_glosa': 0,
            'fecha_vencimiento': 0,
        },
        'emisor': {
            'rut_emisor': str(rut_emisor).lower(),
            'razon_social_emisor':str(razon_social_emisor).lower(),
            'giro_emisor': str(giro_emisor).lower(),
            'dir_emisor': str(dir_emisor).lower(),
            'cmna_emisor': str(cmna_emisor).lower(),
            'ciudad_emisor': str(ciudad_emisor).lower(),
        },
        'receptor': {
            'receptor': str(receptor).lower(),
            'rut_receptor': str(rut_receptor).lower(),
            'razon_social_receptor': str(razon_social_receptor).lower(),
            'giro_receptor': str(giro_receptor).lower(),
            'dir_receptor': str(dir_receptor).lower(),
            'cmna_receptor': str(cmna_receptor).lower(),
            'ciudad_receptor': str(ciudad_receptor).lower(),
        },
        'totales': {
            'neto': utils.format_number(neto),
            'tasa_iva': tasa_iva,
            'iva': utils.format_number(iva),
            'total': utils.format_number(total),
        },
        'detalles': detalles,
        "encoded_file": path
    }
    return data

def generate_pdf417_barcode(string_timbre):
    
    try:
        codes = encode(string_timbre,columns=11)
        svg = render_svg(codes)
        
        tmpfile = tempfile.NamedTemporaryFile(suffix='.svg')
        
        svg.write(tmpfile.name)
        
        return transform_base64(tmpfile.name)
        
    except Exception as err:
        logger.error(f"Error creating PDF417 : {err}")
        return None