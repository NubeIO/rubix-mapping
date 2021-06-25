from abc import abstractmethod

import shortuuid
from flask_restful import marshal_with, reqparse
from rubix_http.exceptions.exception import NotFoundException
from rubix_http.resource import RubixResource

from src.enums.mapping import MappingState, MapType
from src.models.model_lp_gbp_mapping import LPGBPointMapping
from src.resources.rest_schema.schema_lp_gbp_mapping import mapping_lp_gbp_all_fields, mapping_lp_gbp_uuid_attributes, \
    mapping_lp_gbp_name_attributes


def sync_point_value(mapping: LPGBPointMapping):
    # if mapping.mapping_state in (MappingState.MAPPED.name, MappingState.MAPPED):
    #     point_store: PointStoreModel = PointStoreModel.find_by_point_uuid(mapping.point_uuid)
    #     point_store.sync_point_value_lp_to_gbp(mapping.type, mapping.mapped_point_uuid)
    return mapping


class LPGBPMappingResourceList(RubixResource):
    @classmethod
    @marshal_with(mapping_lp_gbp_all_fields)
    def get(cls):
        return LPGBPointMapping.find_all()


class LPGBPMappingResourceListByUUID(RubixResource):
    @classmethod
    @marshal_with(mapping_lp_gbp_all_fields)
    def post(cls):
        parser = reqparse.RequestParser()
        for attr in mapping_lp_gbp_uuid_attributes:
            parser.add_argument(attr,
                                type=mapping_lp_gbp_uuid_attributes[attr].get('type'),
                                required=mapping_lp_gbp_uuid_attributes[attr].get('required', False),
                                default=None)

        data = parser.parse_args()
        data.uuid = str(shortuuid.uuid())
        mapping: LPGBPointMapping = LPGBPointMapping(**data)
        mapping.save_to_db()
        sync_point_value(mapping)
        return mapping


class LPGBPMappingResourceListByName(RubixResource):
    @classmethod
    @marshal_with(mapping_lp_gbp_all_fields)
    def post(cls):
        parser = reqparse.RequestParser()
        for attr in mapping_lp_gbp_name_attributes:
            parser.add_argument(attr,
                                type=mapping_lp_gbp_name_attributes[attr].get('type'),
                                required=mapping_lp_gbp_name_attributes[attr].get('required', False),
                                default=None)

        data = parser.parse_args()
        data.uuid = str(shortuuid.uuid())
        mapping: LPGBPointMapping = LPGBPointMapping(**data)
        mapping.save_to_db()
        sync_point_value(mapping)
        return mapping


class LPGBPMappingResourceUpdateMappingState(RubixResource):
    @classmethod
    def get(cls):
        mappings = LPGBPointMapping.find_all()
        for mapping in mappings:
            try:
                mapping.mapping_state = MappingState.MAPPED
                mapping.check_self()
            except ValueError:
                mapping.mapping_state = MappingState.BROKEN
            mapping.commit()
            sync_point_value(mapping)
        return {"message": "Mapping state has been updated successfully"}


class LPGBPMappingResourceBase(RubixResource):
    @classmethod
    @marshal_with(mapping_lp_gbp_all_fields)
    def get(cls, uuid):
        mapping = cls.get_mapping(uuid)
        if not mapping:
            raise NotFoundException(f'Does not exist {uuid}')
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
    def get_mapping(cls, uuid) -> LPGBPointMapping:
        raise NotImplementedError


class LPGBPMappingResourceByUUID(LPGBPMappingResourceBase):
    parser = reqparse.RequestParser()
    for attr in mapping_lp_gbp_uuid_attributes:
        parser.add_argument(attr,
                            type=mapping_lp_gbp_uuid_attributes[attr].get('type'),
                            required=mapping_lp_gbp_uuid_attributes[attr].get('required', False),
                            default=None)

    @classmethod
    @marshal_with(mapping_lp_gbp_all_fields)
    def patch(cls, uuid):
        data = LPGBPMappingResourceByUUID.parser.parse_args()
        mapping = cls.get_mapping(uuid)
        if not mapping:
            raise NotFoundException(f'Does not exist {uuid}')
        mapping.update(**data)
        sync_point_value(mapping)
        return mapping

    @classmethod
    def get_mapping(cls, uuid) -> LPGBPointMapping:
        return LPGBPointMapping.find_by_uuid(uuid)


class LPGBPMappingResourceByLoRaPointUUID(LPGBPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> LPGBPointMapping:
        return LPGBPointMapping.find_by_point_uuid(uuid)


class LPGBPMappingResourceByGenericPointUUID(LPGBPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> LPGBPointMapping:
        return LPGBPointMapping.find_mapped_point_uuid_type(uuid, MapType.GENERIC)


class LPGBPMappingResourceByBACnetPointUUID(LPGBPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> LPGBPointMapping:
        return LPGBPointMapping.find_mapped_point_uuid_type(uuid, MapType.BACNET)
