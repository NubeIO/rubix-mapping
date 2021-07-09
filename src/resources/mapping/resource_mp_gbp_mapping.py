from abc import abstractmethod

import shortuuid
from flask_restful import marshal_with, reqparse
from rubix_http.exceptions.exception import NotFoundException
from rubix_http.resource import RubixResource

from src.enums.mapping import MappingState, MapType
from src.models.model_mp_gbp_mapping import MPGBPMapping
from src.resources.rest_schema.schema_mpg_bp_mapping import mapping_mp_gbp_all_fields, mapping_mp_gbp_uuid_attributes, \
    mapping_mp_gbp_attributes, mapping_mp_gbp_name_attributes
from src.services.sync_mp_gbp import sync_point_value_with_mapping_mp_to_gbp, get_mp_priority_array_write


def sync_point_value(mapping: MPGBPMapping):
    if mapping.mapping_state in (MappingState.MAPPED.name, MappingState.MAPPED):
        priority_array_write = get_mp_priority_array_write(mapping.point_uuid)
        if priority_array_write:
            sync_point_value_with_mapping_mp_to_gbp(mapping.type, mapping.mapped_point_uuid, priority_array_write)
    return mapping


class MPGBPMappingResourceList(RubixResource):
    @classmethod
    @marshal_with(mapping_mp_gbp_all_fields)
    def get(cls):
        return MPGBPMapping.find_all()


class MPGBPMappingResourceListByUUID(RubixResource):
    @classmethod
    @marshal_with(mapping_mp_gbp_all_fields)
    def post(cls):
        parser = reqparse.RequestParser()
        for attr in mapping_mp_gbp_uuid_attributes:
            parser.add_argument(attr,
                                type=mapping_mp_gbp_attributes[attr].get('type'),
                                required=mapping_mp_gbp_attributes[attr].get('required', False),
                                default=None)
        data = parser.parse_args()
        data.uuid = str(shortuuid.uuid())
        mapping: MPGBPMapping = MPGBPMapping(**data)
        mapping.save_to_db()
        sync_point_value(mapping)
        return mapping


class MPGBPMappingResourceListByName(RubixResource):
    @classmethod
    @marshal_with(mapping_mp_gbp_all_fields)
    def post(cls):
        parser = reqparse.RequestParser()
        for attr in mapping_mp_gbp_name_attributes:
            parser.add_argument(attr,
                                type=mapping_mp_gbp_attributes[attr].get('type'),
                                required=mapping_mp_gbp_attributes[attr].get('required', False),
                                default=None)
        data = parser.parse_args()
        data.uuid = str(shortuuid.uuid())
        mapping: MPGBPMapping = MPGBPMapping(**data)
        mapping.save_to_db()
        sync_point_value(mapping)
        return mapping


class MPGBMappingResourceUpdateMappingState(RubixResource):
    @classmethod
    def get(cls):
        mappings = MPGBPMapping.find_all()
        for mapping in mappings:
            try:
                mapping.mapping_state = MappingState.MAPPED
                mapping.check_self()
            except ValueError:
                mapping.mapping_state = MappingState.BROKEN
            mapping.commit()
            sync_point_value(mapping)
        return {"message": "Mapping state has been updated successfully"}


class MPGBPMappingResourceBase(RubixResource):
    @classmethod
    @marshal_with(mapping_mp_gbp_all_fields)
    def get(cls, uuid):
        mapping = cls.get_mapping(uuid)
        if not mapping:
            raise NotFoundException(f'Does not exist {uuid}')
        return mapping

    @classmethod
    def delete(cls, uuid):
        mapping = cls.get_mapping(uuid)
        if mapping is None:
            raise NotFoundException(f'Does not exist {uuid}')
        mapping.delete_from_db()
        return '', 204

    @classmethod
    @abstractmethod
    def get_mapping(cls, uuid) -> MPGBPMapping:
        raise NotImplementedError


class MPGBPMappingResourceByUUID(MPGBPMappingResourceBase):
    parser = reqparse.RequestParser()
    for attr in mapping_mp_gbp_uuid_attributes:
        parser.add_argument(attr,
                            type=mapping_mp_gbp_attributes[attr].get('type'),
                            required=mapping_mp_gbp_attributes[attr].get('required', False),
                            default=None)

    @classmethod
    @marshal_with(mapping_mp_gbp_all_fields)
    def patch(cls, uuid):
        data = MPGBPMappingResourceByUUID.parser.parse_args()
        mapping: MPGBPMapping = cls.get_mapping(uuid)
        if not mapping:
            raise NotFoundException(f'Does not exist {uuid}')
        mapping.update(**data)
        sync_point_value(mapping)
        return mapping

    @classmethod
    def get_mapping(cls, uuid) -> MPGBPMapping:
        return MPGBPMapping.find_by_uuid(uuid)


class MPGBPMappingResourceByModbusPointUUID(MPGBPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> MPGBPMapping:
        return MPGBPMapping.find_by_point_uuid(uuid)


class MPGBPMappingResourceByGenericPointUUID(MPGBPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> MPGBPMapping:
        return MPGBPMapping.find_by_mapped_point_uuid_type(uuid, MapType.GENERIC)


class MPGBPMappingResourceByBACnetPointUUID(MPGBPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> MPGBPMapping:
        return MPGBPMapping.find_by_mapped_point_uuid_type(uuid, MapType.BACNET)
