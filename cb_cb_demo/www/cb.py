import frappe

no_cache = 1


def get_context(context):
    # Boot data for the SPA (frappe-ui injects window[key] for each entry).
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()  # persist the CSRF token for this session
    context.boot = {"csrf_token": csrf_token, "site_name": frappe.local.site}
