from src.resources.utils import map_rest_schema

mapping_bp_gp_attributes = {
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
    'mapping_state': {
        'type': str,
        'nested': True,
        'dict': 'mapping_state.name',
        'required': True,
    },
}

mapping_bp_gp_uuid_attributes = {
    'point_uuid': {
        'type': str,
        'required': True,
    },
    'mapped_point_uuid': {
        'type': str,
        'required': True,
    },
}

mapping_bp_gp_name_attributes = {
    'point_name': {
        'type': str,
        'required': True,
    },
    'mapped_point_name': {
        'type': str,
        'required': True,
    },
}

mapping_bp_gp_return_attributes = {
    'uuid': {
        'type': str,
    },
}

mapping_bp_gp_all_fields = {}
map_rest_schema(mapping_bp_gp_return_attributes, mapping_bp_gp_all_fields)
map_rest_schema(mapping_bp_gp_attributes, mapping_bp_gp_all_fields)
