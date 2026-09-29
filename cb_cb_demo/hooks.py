app_name = "cb_cb_demo"
app_title = "Mama Oliech Demo"
app_publisher = "CentralBench"
app_description = "Mama Oliech Demo business system"
app_email = "engineering@centralbench.com"
app_license = "Proprietary"

required_apps = ["erpnext"]

# Fixtures are exported with explicit filters only (docs/04 §2.2).
fixtures: list = []

# The Vue frontend is a single-page app under /cb (ADR-0003).
website_route_rules = [{"from_route": "/cb/<path:app_path>", "to_route": "cb"}]
