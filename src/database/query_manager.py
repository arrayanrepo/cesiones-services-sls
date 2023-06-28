## python
import json

## utils
from src.utils import utils

# querys
from src.database import querys


switcher_query = {
    1: querys.insert_aec_file,
    2: querys.insert_certificado_file,
    3: querys.insert_pdf_file
}


def select_query(data, event_type):
    
    payload = {
        'message': 'insert data',
        'event_type': event_type,
        'timestamp': utils.format_date(utils.get_today(),'%d/%m/%Y %H:%M:%S'),
        'data': data
    }
        
    print(json.dumps(payload))
    result = switcher_query.get(int(event_type))(data=data)
    
    return result