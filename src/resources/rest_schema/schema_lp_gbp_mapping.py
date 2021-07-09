from src.resources.utils import map_rest_schema

mapping_lp_gbp_attributes = {
    'point_uuid': {
        'type': str,
        'required': True,
    },
    'mapped_point_uuid': {
        'type': str,
        'required': True,
    },
    'point_name': {
        'type': str,
        'required': True,
    },
    'mapped_point_name': {
        'type': str,
        'required': True,
    },
    'type': {
        'type': str,
        'nested': True,
        'dict': 'type.name',
        'required': True,
    },
    'mapping_state': {
        'type': str,
        'nested': True,
        'dict': 'mapping_state.name',
        'required': True,
    },
}

mapping_lp_gbp_uuid_attributes = {
    'point_uuid': {
        'type': str,
        'required': True,
    },
    'mapped_point_uuid': {
        'type': str,
        'required': True,
    },
    'type': {
        'type': str,
        'nested': True,
        'dict': 'type.name',
        'required': True,
    },
}

mapping_lp_gbp_name_attributes = {
    'point_name': {
        'type': str,
        'required': True,
    },
    'mapped_point_name': {
        'type': str,
        'required': True,
    },
    'type': {
        'type': str,
        'nested': True,
        'dict': 'type.name',
        'required': True,
    },
}

mapping_lp_gbp_return_attributes = {
    'uuid': {
        'type': str,
    },
}

mapping_lp_gbp_all_fields = {}
map_rest_schema(mapping_lp_gbp_return_attributes, mapping_lp_gbp_all_fields)
map_rest_schema(mapping_lp_gbp_attributes, mapping_lp_gbp_all_fields)
