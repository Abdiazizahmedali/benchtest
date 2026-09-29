"""Release marker page (/cb_release) used by CentralBench post-deploy health checks."""

import cb_cb_demo

no_cache = 1


def get_context(context):
	context.no_cache = 1
	context.app_version = cb_cb_demo.__version__
