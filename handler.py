# python
import json
import os
import datetime as dt

## utils
from src.utils import utils

# secrets
from src.secrets import secrets

# cesiones
from src.robots import get_cesiones, get_aec, get_certificados, get_factura_info

# querys
from src.database import querys,query_manager



def get_cesiones_simpli(event, context):

    
    region_secret = os.environ.get('REGION_SECRET')
    secret_name = os.environ.get('SECRET_NAME_SII')

    dias = event['dias']
    tipo_consulta = event['tipo_consulta']

    # get secrets
    _secrets = secrets.get_secrets(secret=secret_name, region=region_secret)
    password = _secrets['pass_sii_simpli']
    rut = _secrets['user_sii_simpli']

    cesiones = get_cesiones.run(rut=rut, password=password, days=dias, tipo_consulta=tipo_consulta)

    payload = {
        'total_cesiones': len(cesiones),
    }

    print(f'EVENT FINISH AT {utils.get_today()} => {payload}')

    return {"statusCode": 200, "body": json.dumps(payload)}


def get_aec_file(event, context):

    
    region_secret = os.environ.get('REGION_SECRET')
    secret_name = os.environ.get('SECRET_NAME_SII')

    # get secrets
    _secrets = secrets.get_secrets(secret=secret_name, region=region_secret)
    password = _secrets['pass_sii_simpli']
    rut = _secrets['user_sii_simpli']

    data = json.loads(event['Records'][0]['Sns']['Message'])

    doc = {
        'folio': int(data['folio']),
        'rut_cliente': data['rut_cliente'],
        'rut_deudor': data['rut_deudor'],
        'tipo_documento': data['tipo_documento']
    }

    url_file = get_aec.run(rut=rut, password=password, documento=doc)

    return {'statuCode': 200, 'url': url_file}


def get_certificado_cesion(event, context):

    region_secret = os.environ.get('REGION_SECRET')
    secret_name = os.environ.get('SECRET_NAME_SII')
    dias = os.environ.get("DAYS")

    # get secrets
    _secrets = secrets.get_secrets(secret=secret_name, region=region_secret)
    password = _secrets['pass_sii_simpli']
    rut = _secrets['user_sii_simpli']

    data = json.loads(event['Records'][0]['Sns']['Message'])

    cesion = {
        'folio': int(data['folio']),
        'rut_cliente': data['rut_cliente'],
        'rut_deudor': data['rut_deudor'],
        'tipo_documento': data['tipo_documento']
    }

    url_file = get_certificados.run(rut=rut, password=password, days=dias, cesion=cesion)

    return {'statuCode': 200, 'url': url_file}


def insert_hc_db(event, context):

    
    data = json.loads(event['Records'][0]['Sns']['Message'])

    cesion = {
        "vendedor": data['rut_cliente'],
        "estado_cesion": data['estado_cesion'],
        "deudor": data['rut_deudor'],
        "mail_deudor": data['mail_deudor'] if "mail_deudor" in data else None,
        "tipo_doc": data['tipo_documento'],
        "nombre_doc": data['nombre_doc'],
        "folio_doc": int(data['folio']),
        "fch_emis_dte": data['fch_emis_dte'],
        "monto_total": data['mnt_total'],
        "cedente": data['cedente'],
        "rz_cedente": data['rz_cedente'],
        "mail_cedente": data['mail_cedente'] if "mail_cedente" in data else None,
        "cesionario": data['cesionario'],
        "rz_cesionario": data['rz_cesionario'],
        "mail_cesionario": data['mail_cesionario'] if "mail_cesionario" in data else None,
        "fecha_cesion": data['fch_cesion'],
        "mnt_cesion": data['mnt_cesion'],
        "fecha_vencimiento": data['fch_vencimiento'],
        "company_id": None,
        "date_created": utils.get_today(),
    }


    result = querys.save_historial_cesion(data=cesion)

    return {"statusCode": 200, 'insert_result': result}


def generatePDFCesion(event, context):

    data = json.loads(event['Records'][0]['Sns']['Message'])
    
    if int(data['event_type']) != 1:
        return {"statusCode": 200, 'url':None} 
        
    aec_record = {
        'rut_cliente': data['rut_cliente'],
        'rut_deudor': data['rut_deudor'],
        'folio': data['folio'],
        'url_file': data['url_file'],
    }
    
    url = get_factura_info.run(data=aec_record)
    
    
    return {"statusCode": 200, 'url':url}

def insert_record_db(event,context):
    
    """Funcion que maneja el proceso de insertado en la base de datos de 
    
        AEC
        Certificado de cesion
        Historial cesiones
        PDF de la factura
    """
    print(f'Event => {event}')
    data = json.loads(event['Records'][0]['Sns']['Message'])

    event_data = {
        'rut_cliente': data['rut_cliente'],
        'rut_deudor': data['rut_deudor'],
        'folio': data['folio'],
        'url_file': data['url_file'],
    }
    
    event_type = data['event_type']

    result = query_manager.select_query(data=event_data, event_type=event_type)

    return {"statusCode": 200, 'result': result}

# def saveAecRegisterDb(event, context):

#     print(f'Event => {event}')
#     data = json.loads(event['Records'][0]['Sns']['Message'])
#     aec_record = {
#         'rut_cliente': data['rut_cliente'],
#         'rut_deudor': data['rut_deudor'],
#         'folio': data['folio'],
#         'url_file': data['url_file'],
#     }

#     result = querys.post_aec_file(data=aec_record)

#     return {"statusCode": 200, 'insert_result': result}
    
    
# def saveCertificadosCesionDb(event, context):

    
#     print(f'Event FINISH  => {event}')
#     data = json.loads(event['Records'][0]['Sns']['Message'])

#     certificado_record = {
#         'rut_cliente': data['rut_cliente'],
#         'rut_deudor': data['rut_deudor'],
#         'folio': data['folio'],
#         'url_file': data['url_file'],
#     }


#     result = querys.insert_certificado_file(data=certificado_record)

#     return {"statusCode": 200, 'insert_result': result}

# def savePDFFactura(event,context):
    
    
#     data = json.loads(event['Records'][0]['Sns']['Message'])
    
#     pdf_record = {
#         'rut_cliente': data['rut_cliente'],
#         'rut_deudor': data['rut_deudor'],
#         'folio': data['folio'],
#         'url_file': data['url_file'],
#     }
    
#     result = querys.savePDFFile(data=pdf_record)
    
#     return {"statusCode": 200, 'insert_result': result}

# if __name__ == '__main__':
    
#     context = {}
#     event = {
#         'Records': [
#             {
#                 'Sns': {
#                     'Message': json.dumps({'rut_cliente':'76105293-4','rut_deudor':'81949100-3','tipo_documento':'33','folio':'7741','url_file':'https://arrayanfilesqa.s3.amazonaws.com/aec_files/30_05_2023/AEC_76105293_4_7741_81949100_3.xml','event_type': 1})
#                 }
#             }
#         ]
#     }
    
#     generatePDFCesion(context=context, event=event)