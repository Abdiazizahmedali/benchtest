"""Boot page for the front end at /cb (ADR-0003). The SPA shell is built into cb.html."""

import frappe

import cb_nairobi_fresh_kitchen_4166

no_cache = 1


def get_context(context):
	# frappe-ui's build injects each boot entry as window[key].
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # persist the CSRF token for this session
	context.boot = {
		"csrf_token": csrf_token,
		"site_name": frappe.local.site,
		"app_version": cb_nairobi_fresh_kitchen_4166.__version__,
	}
