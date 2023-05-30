

# querys
from src.database import querys


switcher_query = {
    1: querys.insert_aec_file,
    2: querys.insert_certificado_file,
    3: querys.insert_pdf_file
}


def select_query(data, event_type):
    
    print(f'TYPE EVENT {event_type}')
    result = switcher_query.get(int(event_type))(data=data)
    
    return result