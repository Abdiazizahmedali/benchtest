"""Release marker page (/cb_release) used by CentralBench post-deploy health checks."""

import cb_nairobi_fresh_kitchen_2a76

no_cache = 1


def get_context(context):
	context.no_cache = 1
	context.app_version = cb_nairobi_fresh_kitchen_2a76.__version__
