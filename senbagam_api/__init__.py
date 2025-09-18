__version__ = '0.0.1'

def after_install():
    import frappe
    frappe.db.set_value("System Settings", "System Settings", "allow_login_using_mobile_number", 1)
