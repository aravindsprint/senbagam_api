import frappe
import re
def uer():
        a=frappe.get_all("Customer",filters={"mobile_no": ["is", "set"],"user":["is","not set"],"name":["!=","mohanasundaram"]},pluck="name")
        print(len(a))
        for i in a:
            b=frappe.get_doc("Customer",i)
        
            user = frappe.new_doc("User")
            c=re.sub(r"\s+", "", b.customer_name).lower()
            c=c.replace(",","")
            c=c.replace(".","")
            e=c+"@sp.com"
            user.email = e
            print(e)
            if not frappe.db.exists('User', e):
                user.first_name =b.customer_name
                user.send_welcome_email = 0
                user.user_type = 'System User'
                user.mobile_no =b.mobile_no
                user.role_profile_name="App User"
                user.save(ignore_permissions=True)
            
                
                frappe.db.set_value(
                    "Customer", i, "user", user.name)
                frappe.db.commit()

                print(user.name)



def user1():
   
    a2=frappe.get_all("Customer",filters={"mobile_no": ["is", "set"],"user":["is","not set"]},pluck="name")
    for i in a2:
        # a=frappe.db.get_value('Customer', {"name":i,}, 'mobile_no')
        try:
            b=frappe.get_doc("User",{"first_name":i})
            if b:
                frappe.db.set_value( "Customer", i, "user", b.name)
                frappe.db.commit()
        except:
            frappe.db.set_value( "Customer", i, "user", "")
            frappe.db.commit()

 
def user3():
     a2=frappe.get_all("User",filters={"mobile_no": ["is", "not set"]},pluck="name")
     for i in a2:
    
      
        try:
            d = frappe.db.get_value("User", i,"first_name")
            f=frappe.get_doc("Customer",{"customer_name":d})
            e = frappe.db.get_value("Customer", f.name,"mobile_no")
            if e:
                frappe.db.set_value( "User", i, "mobile_no", e)
                frappe.db.commit()
        except:
            pass
            # frappe.db.set_value( "User", i, "mobile_no", "")
            # frappe.db.commit()

    



 

