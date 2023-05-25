## python
import datetime as dt

## database con
from src.database.database import DatabaseSession
from src.database import database

database.retrieve_url_conn()

def validate_records(folio,rut_deudor,rut_cliente):
    """Query para validar que no exista la cesion ya en base de datos, esto permitira llamar solo lo necesario cuando se haga el scrapper

    Args:
        folio (string): folio documento
        rut_deudor (string): rut deudor (deudor)
        rut_cliente (rut_cliente): rut cliente (cliente)
    """
    
    DatabaseSession()
    
    sql = """
        SELECT ah.id hist_id, aa.id aec_id, ac.id certf_id 
        from
        api_historialcesiones ah 
        left join api_aeccesion aa on(aa.historialcesion_id = ah.id)
        left join api_cesionesarrayan ac on(ac.rut_deudor = ah.deudor and ac.company_id = ah.company_id and ac.folio = ah.folio_doc)
        where 
        ah.vendedor  =  :rut_cliente 
        and ah.deudor  =  :rut_deudor 
        and ah.folio_doc = :folio
        and ah.cesionario  = '76865845-5'
        order by ah.date_created desc
    """
    result = DatabaseSession.execute_query(query=sql, params={'rut_cliente':rut_cliente, 'rut_deudor':rut_deudor, 'folio': folio})    
    return result

def get_company_id(rut_cliente):
    
    DatabaseSession()
    
    sql = 'SELECT `id` from `api_company` WHERE `rut` = :rut'
    result = DatabaseSession.execute_query(query=sql,params={"rut": rut_cliente})
    return result

def insert_company(rut, business_name):
    
    DatabaseSession()
    
    sql = 'INSERT INTO `api_company` (business_name, rut,date_created) VALUES(:business_name,:rut, :date_created);';
    DatabaseSession.insert_row(sql,params={'rut': rut,'business_name': business_name,'date_created': dt.datetime.now()})
    
def get_historial_cesiones(rut_deudor, folio, company_id):
    
    DatabaseSession()
    
    sql = 'SELECT id FROM api_historialcesiones WHERE company_id = :company_id AND deudor = :deudor AND folio_doc = :folio_doc'
    params = {
        'company_id': company_id,
        'deudor': rut_deudor,
        'folio_doc': folio,
    }
    result = DatabaseSession.execute_query(query=sql, params=params)
    return result

def insert_historial_cesiones(data):
    
    DatabaseSession()
    
    sql = """
        INSERT INTO api_historialcesiones (
            vendedor,
            estado_cesion,
            deudor,
            mail_deudor,
            tipo_doc,
            nombre_doc,
            folio_doc,
            fch_emis_dte,
            monto_total,
            cedente,
            rz_cedente,
            mail_cedente,
            cesionario,
            rz_cesionario,
            mail_cesionario,
            fecha_cesion,
            mnt_cesion,
            fecha_vencimiento,
            date_created,
            company_id
            ) 
        VALUES(
            :vendedor,
            :estado_cesion,
            :deudor,
            :mail_deudor,
            :tipo_doc,
            :nombre_doc,
            :folio_doc,
            :fch_emis_dte,
            :monto_total,
            :cedente,
            :rz_cedente,
            :mail_cedente,
            :cesionario,
            :rz_cesionario,
            :mail_cesionario,
            :fecha_cesion,
            :mnt_cesion,
            :fecha_vencimiento,
            :date_created,
            :company_id
        )
    """
    
    params = {
        "vendedor": data["vendedor"],
        "estado_cesion": data["estado_cesion"], 
        "deudor": data["deudor"],
        "mail_deudor": data["mail_deudor"],
        "tipo_doc": data["tipo_doc"],
        "nombre_doc": data["nombre_doc"],
        "folio_doc": data["folio_doc"],
        "fch_emis_dte": data["fch_emis_dte"],
        "monto_total": data["monto_total"],
        "cedente": data["cedente"],
        "rz_cedente": data["rz_cedente"],
        "mail_cedente": data["mail_cedente"],
        "cesionario": data["cesionario"],
        "rz_cesionario": data["rz_cesionario"],
        "mail_cesionario": data["mail_cesionario"], 
        "fecha_cesion": data["fecha_cesion"], 
        "mnt_cesion": data["mnt_cesion"], 
        "fecha_vencimiento": data["fecha_vencimiento"], 
        "date_created": data["date_created"], 
        "company_id": data["company_id"]
    }
    
    DatabaseSession.insert_row(sql,params=params)
        
def save_historial_cesion(data):

    try:
        results = get_company_id(rut_cliente=data['vendedor'])
        
        if len(results) == 0:
            insert_company(rut=data['vendedor'],business_name=data['rz_cedente'])
            company_id = get_company_id(rut_cliente=data['vendedor'])[0]['id']
            
        company_id = results[0]['id']
        
        ## get db 
        historial_db = get_historial_cesiones(rut_deudor=data['deudor'],folio=data['folio_doc'],company_id=company_id)

        if len(historial_db) > 0:
            return False
        
        ## insertar en historial cesiones
        data['company_id'] = company_id
        insert_historial_cesiones(data=data)
        return True
        
    except Exception as err:
        print(f'Error inserting historial cesiones {err}')
        return False
    
def get_aec_register(historial_cesion_id : int):
    
    DatabaseSession()
    
    sql = 'SELECT id FROM api_aeccesion WHERE historialcesion_id = :id'
    result = DatabaseSession.execute_query(query=sql,params={"id": historial_cesion_id})
    return result

def get_certf_cesion(rut_cliente: str, rut_deudor: str , folio : str):
    
    DatabaseSession()
    
    sql = 'SELECT id FROM api_cesionesarrayan WHERE rut_cliente = :rut_cliente AND rut_deudor = :rut_deudor and folio = :folio'
    params = {
        'rut_cliente': rut_cliente,
        'rut_deudor': rut_deudor,
        'folio': folio,
    }
    result = DatabaseSession.execute_query(query=sql,params=params)
    return result

def insert_db_aec(file,historialcesion_id, date_created):
    
    DatabaseSession()
    
    sql = 'INSERT INTO api_aeccesion (date_created, file, historialcesion_id) VALUES(:date_created, :file, :historialcesion_id)'
    params = {
        'file': file,
        'historialcesion_id': historialcesion_id,
        'date_created': date_created
    }
    
    DatabaseSession.insert_row(sql,params=params)

def insert_certf_cesion(rut_deudor,rut_cliente,company_id,deudor_id,nombre_archivo,folio):
    
    DatabaseSession()
    
    sql = """INSERT INTO arrayan_factoring.api_cesionesarrayan (
        rut_deudor,
        nombre_archivo,
        folio,
        company_id,
        deudor_id,
        rut_cliente,
        date_created
        )
        VALUES(
        :rut_deudor,
        :nombre_archivo,
        :folio,
        :company_id,
        :deudor_id,
        :rut_cliente,
        :date_created
        )"""
    
    params = {
        'rut_cliente':  rut_cliente,
        'rut_deudor': rut_deudor,
        'nombre_archivo': nombre_archivo,
        'folio': folio,
        'company_id': company_id,
        'deudor_id' : deudor_id,
        'date_created': dt.datetime.now(),
    }
    
    DatabaseSession.insert_row(sql,params=params)

def insert_aec_file(data):
    
    
    try:

        results = get_company_id(rut_cliente=data['rut_cliente'])
        company_id = results[0]['id']
        
        ## get db 
        historial_db = get_historial_cesiones(rut_deudor=data['rut_deudor'],folio=data['folio'],company_id=company_id)
        
        if len(historial_db) == 0:
            return False
        
        historial_cesion_id = historial_db[0]['id']
        
        if len(get_aec_register(historial_cesion_id=historial_cesion_id)) > 0:
            return False
        
        insert_db_aec(file=data['url_file'],historialcesion_id=historial_cesion_id,date_created=dt.datetime.now())
        
        return True
        
    except Exception as err:
        print(f'Error aec file {err}')
        return False
    

def insert_certificado_file(data):
    
    try:    
        if len(get_certf_cesion(rut_deudor=data['rut_deudor'],rut_cliente=data['rut_cliente'],folio=data['folio'])) > 0:
            return False
        
        ## get company_id
        results = get_company_id(rut_cliente=data['rut_cliente'])
        company_id = results[0]['id']
        
        ## get deudor_id
        results = get_company_id(rut_cliente=data['rut_deudor'])
        deudor_id = results[0]['id']
        
        insert_certf_cesion(rut_cliente=data['rut_cliente'],rut_deudor=data['rut_deudor'],company_id=company_id,deudor_id=deudor_id,nombre_archivo=data['url_file'],folio=data['folio'])
    
    except Exception as err:
        print(f'Error processing certificate save {err}')
        return False