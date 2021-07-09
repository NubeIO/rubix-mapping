from abc import abstractmethod

import shortuuid
from flask_restful import marshal_with, reqparse
from rubix_http.exceptions.exception import NotFoundException
from rubix_http.resource import RubixResource

from src.enums.mapping import MappingState
from src.models.model_bp_gp_mapping import BPGPointMapping
from src.resources.rest_schema.schema_bp_gp_mapping import mapping_bp_gp_all_fields, mapping_bp_gp_uuid_attributes, \
    mapping_bp_gp_name_attributes
from src.services.sync_bp_gp import sync_point_value_bp_to_gp, get_bp_priority_array_write


def sync_point_value(mapping: BPGPointMapping):
    if mapping.mapping_state in (MappingState.MAPPED.name, MappingState.MAPPED):
        priority_array_write = get_bp_priority_array_write(mapping.point_uuid)
        if priority_array_write:
            sync_point_value_bp_to_gp(mapping.mapped_point_uuid, priority_array_write)
    return mapping


class BPGPMappingResourceList(RubixResource):
    @classmethod
    @marshal_with(mapping_bp_gp_all_fields)
    def get(cls):
        return BPGPointMapping.find_all()


class BPGPMappingResourceListByUUID(RubixResource):
    @classmethod
    @marshal_with(mapping_bp_gp_all_fields)
    def post(cls):
        parser = reqparse.RequestParser()
        for attr in mapping_bp_gp_uuid_attributes:
            parser.add_argument(attr,
                                type=mapping_bp_gp_uuid_attributes[attr].get('type'),
                                required=mapping_bp_gp_uuid_attributes[attr].get('required', False),
                                default=None)

        data = parser.parse_args()
        data.uuid = str(shortuuid.uuid())
        mapping: BPGPointMapping = BPGPointMapping(**data)
        mapping.save_to_db()
        sync_point_value(mapping)
        return mapping


class BPGPMappingResourceListByName(RubixResource):
    @classmethod
    @marshal_with(mapping_bp_gp_all_fields)
    def post(cls):
        parser = reqparse.RequestParser()
        for attr in mapping_bp_gp_name_attributes:
            parser.add_argument(attr,
                                type=mapping_bp_gp_name_attributes[attr].get('type'),
                                required=mapping_bp_gp_name_attributes[attr].get('required', False),
                                default=None)

        data = parser.parse_args()
        data.uuid = str(shortuuid.uuid())
        mapping: BPGPointMapping = BPGPointMapping(**data)
        mapping.save_to_db()
        sync_point_value(mapping)
        return mapping


class BPGPMappingResourceUpdateMappingState(RubixResource):
    @classmethod
    def get(cls):
        mappings = BPGPointMapping.find_all()
        for mapping in mappings:
            try:
                mapping.mapping_state = MappingState.MAPPED
                mapping.check_self()
            except ValueError:
                mapping.mapping_state = MappingState.BROKEN
            mapping.commit()
            sync_point_value(mapping)
        return {"message": "Mapping state has been updated successfully"}


class BPGPMappingResourceBase(RubixResource):
    @classmethod
    @marshal_with(mapping_bp_gp_all_fields)
    def get(cls, uuid):
        mapping = cls.get_mapping(uuid)
        if not mapping:
            raise NotFoundException('Does not exist {uuid}')
        return mapping

    @classmethod
    def delete(cls, uuid):
        mapping = cls.get_mapping(uuid)
        if not mapping:
            raise NotFoundException(f'Does not exist {uuid}')
        mapping.delete_from_db()
        return '', 204

    @classmethod
    @abstractmethod
    def get_mapping(cls, uuid) -> BPGPointMapping:
        raise NotImplementedError


class BPGPMappingResourceByUUID(BPGPMappingResourceBase):
    parser = reqparse.RequestParser()
    for attr in mapping_bp_gp_uuid_attributes:
        parser.add_argument(attr,
                            type=mapping_bp_gp_uuid_attributes[attr].get('type'),
                            required=mapping_bp_gp_uuid_attributes[attr].get('required', False),
                            default=None)

    @classmethod
    @marshal_with(mapping_bp_gp_all_fields)
    def patch(cls, uuid):
        data = BPGPMappingResourceByUUID.parser.parse_args()
        mapping = cls.get_mapping(uuid)
        if not mapping:
            raise NotFoundException(f'Does not exist {uuid}')
        mapping.update(**data)
        sync_point_value(mapping)
        return mapping

    @classmethod
    def get_mapping(cls, uuid) -> BPGPointMapping:
        return BPGPointMapping.find_by_uuid(uuid)


class GBPMappingResourceByGenericPointUUID(BPGPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> BPGPointMapping:
        return BPGPointMapping.find_by_mapped_point_uuid(uuid)


class GBPMappingResourceByBACnetPointUUID(BPGPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> BPGPointMapping:
        return BPGPointMapping.find_by_point_uuid(uuid)
