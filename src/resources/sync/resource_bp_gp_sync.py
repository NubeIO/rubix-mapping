from rubix_http.resource import RubixResource

from src.services.sync_bp_gp import sync_points_values_bp_to_gp_process


class BPToGPSync(RubixResource):

    @classmethod
    def get(cls):
        sync_points_values_bp_to_gp_process()
