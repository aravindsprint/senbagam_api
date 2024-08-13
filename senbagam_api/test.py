import frappe

def test():
    refer="Srinivasan MD"
    refer1=frappe.get_value("Customer",refer,"refered_by")
    print(refer1)
    loyalty=frappe.get_all("Loyalty Point Entry",{"customer":refer})
    for u in loyalty:
        d=frappe.delete_doc("Loyalty Point Entry",u["name"])
        frappe.db.commit()
    v=0
    a=frappe.get_all("Customer",{"refered_by":refer})
    print(a)
    for i in a:
        loyalty=frappe.get_all("Loyalty Point Entry",{"customer":i["name"]})
        for j in loyalty:
            d=frappe.delete_doc("Loyalty Point Entry",j["name"])
            frappe.db.commit()
        sales=frappe.get_all("Sales Invoice",{"customer":i["name"],"status":"Paid"})
        for k in sales:
            s_doc=frappe.get_doc("Sales Invoice",k["name"])
            if s_doc:
                l=frappe.new_doc("Loyalty Point Entry")
                loyalty_points=s_doc.net_total*4/100
                l.customer=refer
                l.invoice_type=s_doc.doctype
                l.invoice=s_doc.name
                l.loyalty_points= loyalty_points
                l.purchase_amount=s_doc.net_total
                l.posting_date=s_doc.posting_date
                l.company=s_doc.company
                l.save(ignore_permissions=True)
            
            if refer1:
                l=frappe.new_doc("Loyalty Point Entry")
                loyalty_points=s_doc.net_total*2/100
                l.customer=refer1
                l.invoice_type=s_doc.doctype
                l.invoice=s_doc.name
                l.loyalty_points= loyalty_points
                l.purchase_amount=s_doc.net_total
                l.posting_date=s_doc.posting_date
                l.company=s_doc.company
                l.save(ignore_permissions=True)
        

        
def test1():
    sales=frappe.get_all("Sales Invoice",{"status":"Paid","posting_date":["between", ["2023-01-01", "2023-08-03"]]})
    try:
        for i in sales:
            sales_doc=frappe.get_doc("Sales Invoice",i["name"])
            refer1=frappe.get_value("Customer",sales_doc.customer,"refered_by")
            refer2=frappe.get_value("Customer",refer1,"refered_by")
            loyalty=frappe.get_all("Loyalty Point Entry",{"customer":refer1})
            for u in loyalty:
                d=frappe.delete_doc("Loyalty Point Entry",u["name"])
                frappe.db.commit()
            loyalty1=frappe.get_all("Loyalty Point Entry",{"customer":refer2})
            for u in loyalty1:
                d=frappe.delete_doc("Loyalty Point Entry",u["name"])
                frappe.db.commit()
            if refer1:
                l=frappe.new_doc("Loyalty Point Entry")
                loyalty_points=sales_doc.net_total*4/100
                l.customer=refer1
                l.invoice_type=sales_doc.doctype
                l.invoice=sales_doc.name
                l.loyalty_points= loyalty_points
                l.purchase_amount=sales_doc.net_total
                l.posting_date=sales_doc.posting_date
                l.company=sales_doc.company
                l.save(ignore_permissions=True)
            if refer2:
                l=frappe.new_doc("Loyalty Point Entry")
                loyalty_points=sales_doc.net_total*2/100
                l.customer=refer2
                l.invoice_type=sales_doc.doctype
                l.invoice=sales_doc.name
                l.loyalty_points= loyalty_points
                l.purchase_amount=sales_doc.net_total
                l.posting_date=sales_doc.posting_date
                l.company=sales_doc.company
                l.save(ignore_permissions=True)
    except:
        pass

