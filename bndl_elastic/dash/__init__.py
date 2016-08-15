from bndl.util import dash
from bndl.util.exceptions import catch
from flask.blueprints import Blueprint
from flask.globals import g
from flask.templating import render_template


blueprint = Blueprint('elastic', __name__,
                      template_folder='templates')


class Status(dash.StatusPanel):
    def render(self):
        return dash.status.DISABLED, render_template('elastic/status.html')


class Dash(dash.Dash):
    blueprint = blueprint
    status_panel_cls = Status


@blueprint.route('/')
def index():
    return render_template('elastic/dashboard.html')
