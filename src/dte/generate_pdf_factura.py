## save 
from src.storage import storage

## jinja
from jinja2 import Environment, FileSystemLoader


def generate_pdf(data,filename,template):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template)
    content = template.render(data)
    return storage.save_file(filename=filename,content=content)