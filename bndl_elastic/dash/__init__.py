# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
