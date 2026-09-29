"""One-time setup of the demo site: ERPNext's own setup wizard (company, currency, country
defaults), then the restaurant menu as Items with selling prices and a walk-in customer.

Runs as a versioned patch during a Release deploy, never as a manual edit on the site. If it
fails, the migration fails and the host restores the previous site (ADR-0002).
"""

import frappe
from frappe.utils import getdate, nowdate

COMPANY = "Mama Oliech Restaurant"
MENU = {
    "Fish": [
        ("TILAPIA-WHOLE", "Whole fried tilapia", "Lake fish, fried crisp, with kachumbari", 1200),
        ("TILAPIA-WET", "Wet-fry tilapia", "Simmered in tomato and onion sauce", 1350),
        ("FISH-FILLET", "Fish fillet", "Pan-seared with lemon butter", 950),
    ],
    "Sides": [
        ("UGALI", "Ugali", "Firm white maize meal", 100),
        ("SUKUMA", "Sukuma wiki", "Sautéed collard greens", 150),
        ("CHIPS", "Chips", "Hand-cut, lightly salted", 200),
    ],
    "Drinks": [
        ("SODA", "Soda", "300 ml, chilled", 80),
        ("PASSION-JUICE", "Fresh passion juice", "Pressed daily", 250),
        ("CHAI", "Chai", "Spiced milk tea", 100),
    ],
}
WALK_IN = "Walk-in Customer"


def execute():
    complete_setup()
    seed_menu()
    seed_walk_in_customer()


def complete_setup():
    if frappe.db.a_row_exists("Company"):
        return
    from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

    year = getdate(nowdate()).year
    result = setup_complete(
        {
            "language": "English",
            "country": "Kenya",
            "timezone": "Africa/Nairobi",
            "currency": "KES",
            "company_name": COMPANY,
            "company_abbr": "MOR",
            "chart_of_accounts": "Standard",
            "fy_start_date": f"{year}-01-01",
            "fy_end_date": f"{year}-12-31",
        }
    )
    if (result or {}).get("status") != "ok" or not frappe.db.a_row_exists("Company"):
        # Fail the migration so the host keeps the previous site.
        raise frappe.ValidationError(f"ERPNext setup did not complete: {result!r}")


def seed_menu():
    price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")
    price_list = price_list or "Standard Selling"
    for group, items in MENU.items():
        if not frappe.db.exists("Item Group", group):
            frappe.get_doc(
                {
                    "doctype": "Item Group",
                    "item_group_name": group,
                    "parent_item_group": "All Item Groups",
                }
            ).insert()
        for code, name, description, rate in items:
            if not frappe.db.exists("Item", code):
                frappe.get_doc(
                    {
                        "doctype": "Item",
                        "item_code": code,
                        "item_name": name,
                        "description": description,
                        "item_group": group,
                        "stock_uom": "Nos",
                        "is_stock_item": 0,
                        "is_sales_item": 1,
                    }
                ).insert()
            if not frappe.db.exists("Item Price", {"item_code": code, "price_list": price_list}):
                frappe.get_doc(
                    {
                        "doctype": "Item Price",
                        "item_code": code,
                        "price_list": price_list,
                        "price_list_rate": rate,
                    }
                ).insert()


def seed_walk_in_customer():
    if frappe.db.exists("Customer", WALK_IN):
        return
    group = frappe.db.get_single_value("Selling Settings", "customer_group")
    territory = frappe.db.get_single_value("Selling Settings", "territory")
    frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": WALK_IN,
            "customer_type": "Individual",
            "customer_group": group or "All Customer Groups",
            "territory": territory or "All Territories",
        }
    ).insert()
