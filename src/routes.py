from flask import Blueprint
from flask_restful import Api

from src.system.resources.ping import Ping
from src.models.model_bp_gp_mapping import BPGPointMapping
from src.models.model_lp_gp_mapping import LPGBPointMapping
from src.models.model_mp_gbp_mapping import MPGBPMapping

bp_system = Blueprint('system', __name__, url_prefix='/api/system')
Api(bp_system).add_resource(Ping, '/ping')


pb_mapping = Blueprint('mapping', __name__, url_prefix='/api/mapping')
