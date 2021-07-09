import json
import logging
from typing import Union, List, Callable

from flask import current_app
from paho.mqtt.client import MQTTMessage
from registry.models.model_device_info import DeviceInfoModel
from registry.resources.resource_device_info import get_device_info
from rubix_mqtt.mqtt import MqttClientBase

from src.enums.driver import Drivers
from src.resources.utils import create_priority_array_write
from src.services.sync_bp_gp import sync_point_value_bp_to_gp_process, sync_point_value_bp_to_mp_process
from src.services.sync_lp_gbp import sync_point_value_lp_to_gbp_process
from src.services.sync_mp_gbp import sync_point_value_gp_to_mp_process, sync_point_value_gp_to_bp_process, \
    sync_point_value_mp_to_gbp_process
from src.setting import MqttSetting

logger = logging.getLogger(__name__)


class MqttListener(MqttClientBase):
    SEPARATOR: str = '/'

    def __init__(self):
        self.__app_context = current_app.app_context
        self.__config: Union[MqttSetting, None] = None
        self.__device_info: Union[DeviceInfoModel, None] = None
        MqttClientBase.__init__(self)

    @property
    def config(self) -> MqttSetting:
        return self.__config

    @property
    def device_info(self) -> Union[DeviceInfoModel, None]:
        return self.__device_info

    def start(self, config: MqttSetting, subscribe_topics: List[str] = None, callback: Callable = lambda: None):
        self.__config = config
        self.__device_info: Union[DeviceInfoModel, None] = get_device_info()
        subscribe_topics: List[str] = [self.__make_topic((self.get_topic_prefix(self.config.topic_ps), '#')),
                                       self.__make_topic((self.get_topic_prefix(self.config.topic_lora), '#')),
                                       self.__make_topic((self.get_topic_prefix(self.config.topic_bacnet), '#'))]
        logger.info(f'Listening at: {subscribe_topics}')
        super().start(config, subscribe_topics, callback)

    def _on_message(self, client, userdata, message: MQTTMessage):
        logger.debug(f'Listener Topic: {message.topic}, Message: {message.payload}')
        if message.payload:
            with self.__app_context():
                if self.get_topic_prefix(self.config.topic_ps) in message.topic:
                    self.__check_and_sync_ps_topic(message)
                if self.get_topic_prefix(self.config.topic_lora) in message.topic:
                    self.__check_and_sync_lora_topic(message)
                if self.get_topic_prefix(self.config.topic_bacnet) in message.topic:
                    self.__check_and_sync_bacnet_topic(message)

    def get_topic_prefix(self, topic: str) -> str:
        return self.__make_topic((
            self.device_info.client_id, self.device_info.client_name, self.device_info.site_id,
            self.device_info.site_name, self.device_info.device_id, self.device_info.device_name, topic
        ))

    @classmethod
    def __make_topic(cls, parts: tuple) -> str:
        return cls.SEPARATOR.join(parts)

    def __mqtt_ps_topic_length(self) -> int:
        return len(self.__make_topic((
            '<client_id>', '<client_name>', '<site_id>', '<site_name>', '<device_id>', '<device_name>',
            self.config.topic_ps, '<driver>', '<network_uuid>', '<network_name>',
            '<device_uuid>', '<device_name>', '<point_uuid>', '<point_name>'
        )).split(self.SEPARATOR))

    def __mqtt_lora_topic_length(self) -> int:
        return len(self.__make_topic((
            '<client_id>', '<client_name>', '<site_id>', '<site_name>', '<device_id>', '<device_name>',
            self.config.topic_lora, '<device_uuid>', '<device_name>'
        )).split(self.SEPARATOR))

    def __mqtt_bacnet_topic_length(self) -> int:
        return len(self.__make_topic((
            '<client_id>', '<client_name>', '<site_id>', '<site_name>', '<device_id>', '<device_name>',
            self.config.topic_bacnet, 'ao', '<object_identifier>', '<point_uuid>', '<point_name>'
        )).split(self.SEPARATOR))

    def __check_and_sync_ps_topic(self, message: MQTTMessage):
        topic: List[str] = message.topic.split(self.SEPARATOR)
        if len(topic) == self.__mqtt_ps_topic_length():
            point_uuid: str = topic[-2]
            driver: str = topic[-7]
            priority_array_write: dict = json.loads(message.payload).get('priority_array')
            if driver == Drivers.GENERIC.name:
                """Generic > Modbus point value"""
                sync_point_value_gp_to_mp_process(point_uuid, priority_array_write)
                """Generic > BACnet point value"""
                sync_point_value_gp_to_bp_process(point_uuid, priority_array_write)
            elif driver == Drivers.MODBUS.name:
                """Modbus > Generic | BACnet point value"""
                sync_point_value_mp_to_gbp_process(point_uuid, priority_array_write)

    def __check_and_sync_lora_topic(self, message: MQTTMessage):
        topic: List[str] = message.topic.split(self.SEPARATOR)
        if len(topic) == self.__mqtt_lora_topic_length():
            payload = json.loads(message.payload)
            for point_name, value in payload.items():
                """LoRa > Generic | BACnet point value"""
                priority_array_write = create_priority_array_write(16, value)
                sync_point_value_lp_to_gbp_process(point_name, priority_array_write)

    def __check_and_sync_bacnet_topic(self, message: MQTTMessage):
        topic: List[str] = message.topic.split(self.SEPARATOR)
        if len(topic) == self.__mqtt_bacnet_topic_length():
            point_uuid: str = topic[-2]
            priority_array_write: dict = json.loads(message.payload).get('priority_array')
            """BACnet > Generic point value"""
            sync_point_value_bp_to_gp_process(point_uuid, priority_array_write)
            """BACnet > Modbus point value"""
            sync_point_value_bp_to_mp_process(point_uuid, priority_array_write)
