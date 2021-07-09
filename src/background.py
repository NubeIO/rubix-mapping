import logging
from threading import Thread

from flask import current_app
from gevent import thread

from .services.sync_bp_gp import sync_points_values_bp_to_gp_process
from .services.sync_lp_gbp import sync_points_values_lp_to_gbp_process
from .services.sync_mp_gbp import sync_points_values_mp_to_gbp_process
from .setting import AppSetting

logger = logging.getLogger(__name__)


class FlaskThread(Thread):
    """
    To make every new thread behinds Flask app context.
    Maybe using another lightweight solution but richer: APScheduler <https://github.com/agronholm/apscheduler>
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = current_app._get_current_object()

    def run(self):
        with self.app.app_context():
            super().run()


class Background:

    @staticmethod
    def run():
        setting: AppSetting = current_app.config[AppSetting.FLASK_KEY]

        # Services
        logger.info("Starting Services...")
        from src.services.mqtt_client.mqtt_listener import MqttListener
        if setting.mqtt_setting.enabled:
            MqttListener().start(setting.mqtt_setting)
        Background.sync_on_start()

    @staticmethod
    def sync_on_start():
        """Sync mapped points values from Modbus > Generic | BACnet points values"""
        logger.info("Starting Sync Modbus > Generic | BACnet...")
        sync_points_values_mp_to_gbp_process()

        """Sync mapped points values from BACnet > Generic points values"""
        logger.info("Starting Sync BACnet > Generic...")
        sync_points_values_bp_to_gp_process()

        """Sync mapped points values from LoRa > Generic | BACnet points values"""
        logger.info("Starting Sync LoRa > Generic | BACnet...")
        sync_points_values_lp_to_gbp_process()
