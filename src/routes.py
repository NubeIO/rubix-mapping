from flask import Blueprint
from flask_restful import Api

from src.resources.resource_bp_gp_mapping import BPGPMappingResourceList, BPGPMappingResourceListByUUID, \
    BPGPMappingResourceListByName, BPGPMappingResourceByUUID, GBPMappingResourceByBACnetPointUUID, \
    GBPMappingResourceByGenericPointUUID, BPGPMappingResourceUpdateMappingState
from src.resources.resource_lp_gbp_mapping import LPGBPMappingResourceList, LPGBPMappingResourceListByUUID, \
    LPGBPMappingResourceListByName, LPGBPMappingResourceByUUID, LPGBPMappingResourceByLoRaPointUUID, \
    LPGBPMappingResourceByGenericPointUUID, LPGBPMappingResourceByBACnetPointUUID, \
    LPGBPMappingResourceUpdateMappingState
from src.resources.resource_mpg_bp_mapping import MPGBPMappingResourceList, MPGBPMappingResourceListByUUID, \
    MPGBPMappingResourceListByName, MPGBPMappingResourceByUUID, MPGBPMappingResourceByModbusPointUUID, \
    MPGBPMappingResourceByGenericPointUUID, MPGBPMappingResourceByBACnetPointUUID, MPGBMappingResourceUpdateMappingState
from src.system.resources.ping import Ping

bp_system = Blueprint('system', __name__, url_prefix='/api/system')
Api(bp_system).add_resource(Ping, '/ping')

# Modbus <> Generic|BACnet points mappings
bp_mapping_mp_gbp = Blueprint('mappings_mp_gbp', __name__, url_prefix='/api/mappings/mp_gbp')
api_mapping_mp_gbp = Api(bp_mapping_mp_gbp)
api_mapping_mp_gbp.add_resource(MPGBPMappingResourceList, '')
api_mapping_mp_gbp.add_resource(MPGBPMappingResourceListByUUID, '/uuid')
api_mapping_mp_gbp.add_resource(MPGBPMappingResourceListByName, '/name')
api_mapping_mp_gbp.add_resource(MPGBPMappingResourceByUUID, '/uuid/<string:uuid>')
api_mapping_mp_gbp.add_resource(MPGBPMappingResourceByModbusPointUUID, '/modbus/<string:uuid>')
api_mapping_mp_gbp.add_resource(MPGBPMappingResourceByGenericPointUUID, '/generic/<string:uuid>')
api_mapping_mp_gbp.add_resource(MPGBPMappingResourceByBACnetPointUUID, '/bacnet/<string:uuid>')
api_mapping_mp_gbp.add_resource(MPGBMappingResourceUpdateMappingState, '/update_mapping_state')

# lora to generic/bacnet points mappings
bp_mapping_lp_gbp = Blueprint('mappings_lp_gbp', __name__, url_prefix='/api/mappings/lp_gbp')
api_mapping_lp_gbp = Api(bp_mapping_lp_gbp)
api_mapping_lp_gbp.add_resource(LPGBPMappingResourceList, '')
api_mapping_lp_gbp.add_resource(LPGBPMappingResourceListByUUID, '/uuid')
api_mapping_lp_gbp.add_resource(LPGBPMappingResourceListByName, '/name')
api_mapping_lp_gbp.add_resource(LPGBPMappingResourceByUUID, '/uuid/<string:uuid>')
api_mapping_lp_gbp.add_resource(LPGBPMappingResourceByLoRaPointUUID, '/lora/<string:uuid>')
api_mapping_lp_gbp.add_resource(LPGBPMappingResourceByGenericPointUUID, '/generic/<string:uuid>')
api_mapping_lp_gbp.add_resource(LPGBPMappingResourceByBACnetPointUUID, '/bacnet/<string:uuid>')
api_mapping_lp_gbp.add_resource(LPGBPMappingResourceUpdateMappingState, '/update_mapping_state')

# BACnet points <> Generic points mappings
bp_mapping_bp_gp = Blueprint('mappings_bp_gp', __name__, url_prefix='/api/mappings/bp_gp')
api_mapping_bp_gp = Api(bp_mapping_bp_gp)
api_mapping_bp_gp.add_resource(BPGPMappingResourceList, '')
api_mapping_bp_gp.add_resource(BPGPMappingResourceListByUUID, '/uuid')
api_mapping_bp_gp.add_resource(BPGPMappingResourceListByName, '/name')
api_mapping_bp_gp.add_resource(BPGPMappingResourceByUUID, '/uuid/<string:uuid>')
api_mapping_bp_gp.add_resource(GBPMappingResourceByBACnetPointUUID, '/bacnet/<string:uuid>')
api_mapping_bp_gp.add_resource(GBPMappingResourceByGenericPointUUID, '/generic/<string:uuid>')
api_mapping_bp_gp.add_resource(BPGPMappingResourceUpdateMappingState, '/update_mapping_state')
