from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

BASE_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas", "templates")

def render_template(template_name: str, context: dict, lang: str = "en") -> str:
    """
    Renders an HTML template based on selected language.
    """
    try:
        lang_dir = os.path.join(BASE_TEMPLATE_DIR, lang)
        env = Environment(
            loader=FileSystemLoader(lang_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template(template_name)
        return template.render(context)
    except Exception as e:
        print(f"Template render error [{lang}/{template_name}]: {e}")
        raise
