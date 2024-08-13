import frappe
import re
import random
def user_creation(self,event):
    if self.mobile_no1 and not frappe.db.exists("User", {"mobile_no": self.mobile_no1}):
        user = frappe.new_doc("User")
        random_number = random.randint(1000, 9999)
        customer_id = self.customer_name + str(random_number)
        b=re.sub(r"\s+", "", customer_id).lower()
        e=b+"@sps.com"
        user.email = e

        user.first_name =self.customer_name
        user.send_welcome_email = 0
        user.user_type = 'System User'
        user.mobile_no =self.mobile_no1
        user.username=self.name
        user.role_profile_name="App User"
        user.save(ignore_permissions=True)
        self.user=user.name
        self.save()
        # # user.new_password = args["password"]
        # user.save(ignore_permissions = True)

