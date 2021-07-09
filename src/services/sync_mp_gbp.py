"""
modbus_point <> generic_point | bacnet_point
"""
import json
from typing import List

import gevent
from flask import Response
from rubix_http.method import HttpMethod
from rubix_http.request import gw_request

from src.enums.mapping import MapType, MappingState
from src.models.model_bp_gp_mapping import BPGPointMapping
from src.models.model_mp_gbp_mapping import MPGBPMapping
from src.resources.utils import create_priority_array_write


def get_mp_priority_array_write(point_uuid):
    response: Response = gw_request(api=f'/ps/api/modbus/points/uuid/{point_uuid}')
    if response.status_code == 200:
        priority_array_write = json.loads(response.data).get('priority_array_write')
        if not priority_array_write:
            value = json.loads(response.data).get('point_store', {}).get('value')
            priority_array_write = create_priority_array_write(16, value)
        return priority_array_write
    return None


def sync_point_value_gp_to_mp(modbus_point_uuid: str, priority_array_write: dict):
    gw_request(
        api=f"/ps/api/modbus/points_value/uuid/{modbus_point_uuid}",
        body={"priority_array_write": priority_array_write},
        http_method=HttpMethod.PATCH
    )


def sync_point_value_gp_to_mp_process(point_uuid, priority_array_write: dict):
    mapping: MPGBPMapping = MPGBPMapping.find_by_mapped_point_uuid_type(point_uuid, MapType.GENERIC)
    if mapping and mapping.mapping_state == MappingState.MAPPED:
        gevent.spawn(sync_point_value_gp_to_mp, mapping.point_uuid, priority_array_write)


def sync_point_value_gp_to_bp(point_uuid, priority_array_write: dict):
    gw_request(
        api=f"/bacnet/api/bacnet/points/uuid/{point_uuid}",
        body={"priority_array_write": priority_array_write},
        http_method=HttpMethod.PATCH
    )


def sync_point_value_gp_to_bp_process(point_uuid, priority_array_write: dict):
    mapping: BPGPointMapping = BPGPointMapping.find_by_mapped_point_uuid(point_uuid)
    if mapping and mapping.mapping_state == MappingState.MAPPED:
        gevent.spawn(sync_point_value_gp_to_bp, mapping.point_uuid, priority_array_write)


def sync_point_value_with_mapping_mp_to_gbp(map_type: str, point_uuid: str, priority_array_write: dict,
                                            gp: bool = True, bp: bool = True, ):
    if map_type in (MapType.GENERIC.name, MapType.GENERIC) and gp:
        gw_request(
            api=f"/ps/api/generic/points_value/uuid/{point_uuid}",
            body={'priority_array_write': priority_array_write},
            http_method=HttpMethod.PATCH
        )
    elif map_type in (MapType.BACNET.name, MapType.BACNET) and bp:
        gw_request(
            api=f"/bacnet/api/bacnet/points/uuid/{point_uuid}",
            body={"priority_array_write": priority_array_write},
            http_method=HttpMethod.PATCH
        )


def sync_point_value_mp_to_gbp_process(point_uuid, priority_array_write: dict, gp: bool = True, bp: bool = True):
    mapping: MPGBPMapping = MPGBPMapping.find_by_point_uuid(point_uuid)
    if mapping and mapping.mapping_state == MappingState.MAPPED:
        gevent.spawn(
            sync_point_value_with_mapping_mp_to_gbp,
            mapping.type, mapping.mapped_point_uuid, priority_array_write,
            gp, bp
        )


def sync_points_values_mp_to_gbp_process(gp: bool = True, bp: bool = True):
    mappings: List[MPGBPMapping] = MPGBPMapping.find_all()
    for mapping in mappings:
        if mapping.mapping_state == MappingState.MAPPED and (gp and mapping.type == MapType.GENERIC) \
                or (bp and mapping.type == MapType.BACNET):
            priority_array_write = get_mp_priority_array_write(mapping.point_uuid)
            if priority_array_write:
                sync_point_value_mp_to_gbp_process(mapping.point_uuid, priority_array_write, gp=gp, bp=bp)
