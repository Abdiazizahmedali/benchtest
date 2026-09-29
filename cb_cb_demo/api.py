"""Whitelisted endpoints for the front-of-house app. Permissions are the signed-in user's
(no ignore_permissions); prices come from the ERP, never from the browser."""

import frappe
from frappe import _
from frappe.utils import nowdate

WALK_IN = "Walk-in Customer"


@frappe.whitelist(methods=["POST"])
def place_order(table: str, lines: list | str) -> dict:
    lines = frappe.parse_json(lines) if isinstance(lines, str) else lines
    if not lines:
        frappe.throw(_("The order is empty."))
    if len(table or "") > 20:
        frappe.throw(_("Invalid table."))
    price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")
    items = []
    for line in lines:
        code, qty = line.get("item_code"), int(line.get("qty") or 0)
        if qty < 1 or qty > 99 or not frappe.db.exists("Item", {"name": code, "is_sales_item": 1}):
            frappe.throw(_("Invalid item in the order."))
        rate = frappe.db.get_value(
            "Item Price", {"item_code": code, "price_list": price_list}, "price_list_rate"
        )
        items.append({"item_code": code, "qty": qty, "rate": rate or 0, "delivery_date": nowdate()})
    order = frappe.get_doc(
        {
            "doctype": "Sales Order",
            "customer": WALK_IN,
            "order_type": "Sales",
            "transaction_date": nowdate(),
            "delivery_date": nowdate(),
            "po_no": table,
            "items": items,
        }
    )
    order.insert()  # checks the user's create permission on Sales Order
    return {"name": order.name, "grand_total": order.grand_total, "currency": order.currency}
