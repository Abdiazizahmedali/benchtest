app_name = "cb_spike"
app_title = "CB Spike"
app_publisher = "CentralBench"
app_description = "CB Spike business system"
app_email = "engineering@centralbench.com"
app_license = "Proprietary"

required_apps = ["erpnext"]

# Fixtures are exported with explicit filters only (docs/04 §2.2).
fixtures: list = []

# The Vite frontend is a single-page app under /cb.
website_route_rules = [{"from_route": "/cb/<path:app_path>", "to_route": "cb"}]
