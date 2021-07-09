"""
lora_point <> generic_point | bacnet_point
"""
import json
from typing import List

import gevent
from flask import Response
from rubix_http.method import HttpMethod
from rubix_http.request import gw_request

from src.enums.mapping import MapType, MappingState
from src.models.model_lp_gbp_mapping import LPGBPointMapping
from src.resources.utils import create_priority_array_write


def get_lp_priority_array_write(point_uuid):
    response: Response = gw_request(api=f'/lora/api/lora/points/uuid/{point_uuid}')
    if response.status_code == 200:
        value = json.loads(response.data).get('point_store', {}).get('value')
        return create_priority_array_write(16, value)
    return None


def sync_point_value_lp_to_gbp(map_type: str, point_uuid: str, priority_array_write: dict, gp: bool = True,
                               bp=True):
    if map_type in (MapType.GENERIC.name, MapType.GENERIC) and gp:
        gw_request(
            api=f"/ps/api/generic/points_value/uuid/{point_uuid}",
            body={"priority_array_write": priority_array_write},
            http_method=HttpMethod.PATCH
        )
    elif map_type in (MapType.BACNET.name, MapType.BACNET) and bp:
        gw_request(
            api=f"/bacnet/api/bacnet/points/uuid/{point_uuid}",
            body={"priority_array_write": priority_array_write},
            http_method=HttpMethod.PATCH
        )


def sync_point_value_lp_to_gbp_process(point_name, priority_array_write: dict, gp: bool = True, bp=True):
    mapping: LPGBPointMapping = LPGBPointMapping.find_by_point_name(point_name)
    if mapping and mapping.mapping_state == MappingState.MAPPED:
        gevent.spawn(sync_point_value_lp_to_gbp,
                     mapping.type, mapping.mapped_point_uuid, priority_array_write, gp, bp)


def sync_points_values_lp_to_gbp_process(gp: bool = True, bp=True):
    mappings: List[LPGBPointMapping] = LPGBPointMapping.find_all()
    for mapping in mappings:
        if mapping.mapping_state == MappingState.MAPPED and (gp and mapping.type == MapType.GENERIC) \
                or (bp and mapping.type == MapType.BACNET):
            priority_array_write = get_lp_priority_array_write(mapping.point_uuid)
            if priority_array_write:
                sync_point_value_lp_to_gbp_process(mapping.point_name, priority_array_write, gp=gp, bp=bp)
