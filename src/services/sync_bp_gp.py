"""
bacnet_point <> generic_point
"""
import json
from typing import List

import gevent
from flask import Response
from rubix_http.method import HttpMethod
from rubix_http.request import gw_request

from src.enums.mapping import MappingState, MapType
from src.models.model_bp_gp_mapping import BPGPointMapping
from src.models.model_mp_gbp_mapping import MPGBPMapping
from src.resources.utils import create_priority_array_write


def get_bp_priority_array_write(point_uuid):
    response: Response = gw_request(api=f'/bacnet/api/bacnet/points/uuid/{point_uuid}')
    if response.status_code == 200:
        priority_array_write = json.loads(response.data).get('priority_array_write')
        if not priority_array_write:
            value = json.loads(response.data).get('point_store', {}).get('value')
            priority_array_write = create_priority_array_write(16, value)
        return priority_array_write


def sync_point_value_bp_to_gp(point_uuid: str, priority_array_write: dict):
    gw_request(
        api=f"/ps/api/generic/points_value/uuid/{point_uuid}",
        body={"priority_array_write": priority_array_write},
        http_method=HttpMethod.PATCH
    )


def sync_point_value_bp_to_gp_process(point_uuid, priority_array_write: dict):
    mapping: BPGPointMapping = BPGPointMapping.find_by_point_uuid(point_uuid)
    if mapping and mapping.mapping_state == MappingState.MAPPED:
        gevent.spawn(sync_point_value_bp_to_gp, mapping.mapped_point_uuid, priority_array_write)


def sync_point_value_bp_to_mp(point_uuid, priority_array_write: dict):
    gw_request(
        api=f"/ps/api/modbus/points_value/uuid/{point_uuid}",
        body={"priority_array_write": priority_array_write},
        http_method=HttpMethod.PATCH
    )


def sync_point_value_bp_to_mp_process(point_uuid, priority_array_write: dict):
    mapping: MPGBPMapping = MPGBPMapping.find_by_mapped_point_uuid_type(point_uuid, MapType.BACNET)
    if mapping and mapping.mapping_state == MappingState.MAPPED:
        gevent.spawn(sync_point_value_bp_to_mp, mapping.point_uuid, priority_array_write)


def sync_points_values_bp_to_gp_process():
    mappings: List[BPGPointMapping] = BPGPointMapping.find_all()
    for mapping in mappings:
        if mapping.mapping_state == MappingState.MAPPED:
            priority_array_write = get_bp_priority_array_write(mapping.point_uuid)
            if priority_array_write:
                sync_point_value_bp_to_mp_process(mapping.point_uuid, priority_array_write)
