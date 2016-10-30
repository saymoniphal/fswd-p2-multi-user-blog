import os.path

import bleach
import markupsafe
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def do_clean(text, **kw):
    """Perform clean and return a Markup object to mark the string as safe.
    This prevents Jinja from re-escaping the result."""
    return markupsafe.Markup(bleach.clean(text, **kw))

jinja_env.filters['clean'] = do_clean

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
