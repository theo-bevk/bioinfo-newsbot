from jinja2 import Environment, FileSystemLoader
from datetime import datetime
def render_html(items):
    env = Environment(loader=FileSystemLoader("templates"))
    tmpl = env.get_template("email.html.j2")
    return tmpl.render(items=items, date_human=datetime.now().strftime("%b %d, %Y"))
