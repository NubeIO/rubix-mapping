from rubix_http.resource import RubixResource

from src.services.sync_mp_gbp import sync_points_values_mp_to_gbp_process


class MPToGPSync(RubixResource):

    @classmethod
    def get(cls):
        sync_points_values_mp_to_gbp_process(gp=True, bp=False)


class MPToBPSync(RubixResource):

    @classmethod
    def get(cls):
        sync_points_values_mp_to_gbp_process(gp=False, bp=True)


class MPToGBPSync(RubixResource):

    @classmethod
    def get(cls):
        sync_points_values_mp_to_gbp_process(gp=True, bp=True)
