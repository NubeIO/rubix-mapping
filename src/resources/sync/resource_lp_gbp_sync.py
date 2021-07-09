from rubix_http.resource import RubixResource

from src.services.sync_lp_gbp import sync_points_values_lp_to_gbp_process


class LPToGPSync(RubixResource):

    @classmethod
    def get(cls):
        sync_points_values_lp_to_gbp_process(gp=True, bp=False)


class LPToBPSync(RubixResource):

    @classmethod
    def get(cls):
        sync_points_values_lp_to_gbp_process(gp=False, bp=True)


class LPToGBPSync(RubixResource):

    @classmethod
    def get(cls):
        sync_points_values_lp_to_gbp_process(gp=True, bp=True)
