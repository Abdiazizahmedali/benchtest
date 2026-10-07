app_name = "cb_nairobi_fresh_kitchen_2a76"
app_title = "Nairobi Fresh Kitchen"
app_publisher = "CentralBench"
app_description = "Nairobi Fresh Kitchen business system"
app_email = "engineering@centralbench.com"
app_license = "Proprietary"

required_apps = ["erpnext"]

# Fixtures are exported with explicit filters only (docs/04 §2.2).
fixtures: list = []

# The front end is a single-page app under /cb (ADR-0003).
website_route_rules = [{"from_route": "/cb/<path:app_path>", "to_route": "cb"}]
