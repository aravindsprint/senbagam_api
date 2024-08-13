import frappe



# @frappe.whitelist(allow_guest=True)
def itemlist(self,events):
   
    item_list= frappe.get_all("Item",filters={"app_priority":[">=",self.app_priority],"item_group":self.item_group},pluck="name")
   
    for i in item_list:
         actual_priority=frappe.db.get_value("Item",i,"app_priority")
         frappe.db.set_value("Item",i, "app_priority", actual_priority+1)
         frappe.db.commit()



