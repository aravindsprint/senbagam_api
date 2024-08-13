import frappe
import random as r
import requests
from datetime import date, datetime
from json import loads
# from frappe.core.doctype.user.user import generate_keys

import json
@frappe.whitelist( allow_guest=True )
def add_image():
	return frappe.request.data

# @frappe.whitelist( allow_guest=True )
# def login(args):
#     data={}
#     # args=json.loads(args)
#     try:
#         login_manager = frappe.auth.LoginManager()
#         login_manager.authenticate(user=args["username"], pwd=args["password"])
#         login_manager.post_login()
#     except frappe.exceptions.AuthenticationError:
#         frappe.clear_messages()
#         frappe.local.response["message"] = {
#             "key":0,
#             "message":"Incorrect Username or Password"
#         }
#         return
#     api_generate = generate_keys(frappe.session.user)
#     # return api_generate
#     frappe.db.commit()


#     user = frappe.get_doc('User', frappe.session.user)
#     if user:
#         data.update({"key":1})
#         data.update({"message":"Logged in"})
#         data.update({"api_key":user.api_key})
#         data.update({"api_secret":api_generate["api_secret"]})
#         data.update({"name":user.full_name})
#         data.update({"dob":user.birth_date})
#         data.update({"mobile_no":user.mobile_no})
#         data.update({"email":user.email})
#         data.update({"welcome": welcome()["content"]})
#         data.update({"store": store()["content"]})
#         data.update({"roles":[i[0] for i in frappe.db.sql("""SELECT DISTINCT a.role FROM `tabHas Role` as a inner join `tabUser` as b on a.parent = b.name  WHERE a.parent = '{0}'""".format(user.name),as_list=1)]})


#     cust = frappe.db.get_value("Customer", {"user": user.name}, "name")
#     customer = frappe.get_doc("Customer", cust)
#     try:
#         data.update({"customer_name":customer.name})
#         data.update({"gstin":customer.gstin or ""})
#         data.update({"customer_doc_name":customer.name})
#         data.update({"refered_by":customer.refered_by or ""})
#     except:
#         data.update({"customer_name":""})
#         data.update({"gstin":""})
#         data.update({"customer_doc_name":""})
#         data.update({"refered_by":""})

#     if customer.customer_primary_address:
#         address = frappe.get_doc("Address", customer.customer_primary_address)
#         try:

#             data.update({"address":address.address_line1 or ""})
#             data.update({"city":address.city or ""})
#             data.update({"district": address.district or ""})
#             data.update({"pincode":address.pincode or ""})
#         except:
#             data.update({"address":""})
#             data.update({"city":""})
#             data.update({"district":""})
#             data.update({"pincode":""})
#     else:
#         data.update({"address":""})
#         data.update({"city":""})
#         data.update({"district":""})
#         data.update({"pincode":""})


#     return data


@frappe.whitelist(allow_guest=True )
def login(args):
	
	if isinstance(args, str):
		args=json.loads(args)

	try:
		frappe.flags.mobile_login = True
		login_manager = frappe.auth.LoginManager()
		login_manager.authenticate(user=args["username"], pwd=args["password"])
		login_manager.post_login()
	except frappe.exceptions.AuthenticationError:
		frappe.clear_messages()
		# frappe.local.response.http_status_code = 403
		frappe.local.response["message"] = {
			"key":0,
			"message":"Incorrect Username or Password"
		}
		frappe.flags.mobile_login = False
		return
	frappe.flags.mobile_login = False
	api_generate = generate_keys(frappe.session.user)
	frappe.db.commit()
	user = frappe.get_doc('User', frappe.session.user)

	cust = frappe.db.get_value("Customer", {"user": user.name}, "name")
	customer = frappe.get_doc("Customer", cust)

	#    address = frappe.get_doc("Address", customer.customer_primary_address)



	frappe.response["message"] = {
		"key":1,
		"message":"Logged in",
		#"sid":frappe.session.sid,
		"api_key":user.api_key,
		"api_secret":api_generate["api_secret"],
		"name":customer.name,
		"dob":user.birth_date or "",
		"customer_name":customer.name or "",
		"mobile_no":user.mobile_no,
		"email":user.email,
		"address": "",
		"city":"",
		"district": "",
		"refered_by":"",
		"gstin":"",
		"customer_doc_name":customer.name,
		"pincode":"",
		"roles": [i[0] for i in frappe.db.sql("""SELECT DISTINCT a.role FROM `tabHas Role` as a inner join `tabUser` as b on a.parent = b.name  WHERE a.parent = '{0}'""".format(user.name),as_list=1)],
		"welcome": welcome()["content"],
		"store": store()["content"],
		"upi_no":customer.upi_number or ""
	}



def generate_keys(user):
	"""
	generate api key and api secret

	:param user: str
	"""
	# frappe.only_for("System Manager")
	user_details = frappe.get_doc("User", user)
	api_secret = frappe.generate_hash(length=15)
	# if api key is not set generate api key
	if not user_details.api_key:
		api_key = frappe.generate_hash(length=15)
		user_details.api_key = api_key
	user_details.api_secret = api_secret
	user_details.save()

	return {"api_secret": api_secret}



@frappe.whitelist()
def logout():
	api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
	user = frappe.db.get_value("User", {"api_key": api_key})

	login_manager = frappe.auth.LoginManager()
	login_manager.logout(user = user)
	generate_keys(user)
	frappe.db.set_value("User",user.name,"enabled",1)
	frappe.db.commit()
	return {"message": "Successfully Logged Out"}

@frappe.whitelist(allow_guest=True)
def send_otp(args):
	mobile_no = args["mobile_no"]
	message = "Not Success"
	if frappe.db.get_value("User", {"mobile_no": mobile_no}):
		message = "Success"
	return {
		"message": message
		}

# @frappe.whitelist(allow_guest=True)
# def reset_password(args):
#    otp = args["otp"]
#    new_password = args["new_password"]
#    return {
#        "message": "Success"
	#    }

from frappe.utils.password import update_password
@frappe.whitelist(allow_guest=True)
def reset_password(args):
	# args=json.loads(args)
	user=frappe.get_doc("User",{"mobile_no":args["mobile_no"]})
	if args["original_otp"]==args["enter_otp"]:
		# user.new_password =args["new_password"]
		update_password(user=user.name, pwd=args["new_password"],logout_all_sessions=False)
		# frappe.db.set_value("User",user.name,"new_password",args["new_password"])
		# user.save(ignore_permissions=True)
		frappe.db.set_value("User",user.name,"enabled",1)
		frappe.db.commit()
		return {"message":"Password Reset Successfully"}
	else:
		return {"message":"Incorrect OTP or mobile no"}





@frappe.whitelist()
def add_referral(args):
	api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
	name = args["name"]
	mobile_no = args["mobile_no"]
	doc = frappe.new_doc("Referral")
	doc.refered_by = frappe.db.get_value("User", {"api_key": api_key})
	doc.person_name = name
	doc.person_mobile = mobile_no
	doc.save(ignore_permissions=True)
	msg = "Hey! Get your discount on every order by installing the app"
	system_msg = frappe.db.get_value("App Settings", "App Settings", "share_message")
	if system_msg:
		msg = system_msg
	return{
		"message": "Success",
		"share": msg
	}


@frappe.whitelist(allow_guest=True)
def get_referrals(args):
	#    args=json.loads(args)
	mobile_no = args["mobile_no"]
	#    return mobile_no
	referred_by = frappe.db.sql(""" select CONCAT(c.customer_name)  from `tabCustomer` as c join `tabReferral` as r on c.user=r.refered_by join `tabUser` as u on c.user=u.name where r.person_mobile='{0}' """.format(mobile_no), as_list=1)

	referred_by = [i[0] for i in referred_by] or ["Senbagam Paints"]
	return {
		"message": "Success",
		"refered_by": referred_by,
		"length": len(referred_by),
		}

@frappe.whitelist(allow_guest=True)
def signup(args):
	frappe.session.user = "Administrator"
	# args=json.loads(args)
	data = {"message":""}
	if not args["name"]:
		data["message"] = "Name cannot be null"
		return data

	if not args["mobile_no"]:
		data["message"] = "Mobile No cannot be null"
		return data

	if not args["email"]:
		data["message"] = "Email cannot be null"
		return data

	if not args["password"]:
		data["message"] = "Password cannot be null"
		return data

	if frappe.db.get_value("User", args["email"]):
		data["message"] = "Email Id Already Exists"
		return data

	frappe.log_error(title="MOBILE", message = args["mobile_no"])
	if frappe.db.get_value("User", {"mobile_no": args["mobile_no"]}):
		data["message"] = "Mobile No Already Exists"
		return data
	if args["referral_code"]:
		if not frappe.db.exists("User", {"referral_id": args["referral_code"]}):
			data["message"] = "Referral code not recognized"
			return data

	user = frappe.new_doc("User")
	user.email = args["email"]
	user.first_name = args["name"]
	user.send_welcome_email = 0
	user.user_type = 'System User'
	user.mobile_no = args["mobile_no"]
	if args["dob"]:
		user.birth_date = args["dob"]
		user.role_profile_name="App User"
	user.save(ignore_permissions=True)
	user.new_password = args["password"]
	user.save(ignore_permissions = True)

	if args["referral_code"]:
		referral_doc=frappe.new_doc("Referral")
		if frappe.db.get_value("User", {"referral_id": args["referral_code"]}):
			referral_id=frappe.db.get_value("User", {"referral_id": args["referral_code"]})
			referral_doc.refered_by=referral_id
		
		referral_doc.person_name=args["name"]
		referral_doc.person_mobile=args["mobile_no"]
		referral_doc.save(ignore_permissions=True)
	#    user.add_roles('System Manager')
	if not frappe.db.exists("Customer",{"mobile_no":args["mobile_no"]}):
		customer = frappe.new_doc("Customer")
		customer.customer_name = args["name"]
		customer.customer_type = "Individual"
		customer.mobile_no1=args["mobile_no"]
		customer.customer_group = "Individual"
		customer.territory = "India"
		if args["upi_no"]:	
			customer.upi_number = args["upi_no"]
		if args["gstin"]:
			customer.gstin = args["gstin"]
			customer.gst_category="Registered Regular"
		# if args["refered_by"]:
		# 	customer.refered_by = args["refered_by"]
		customer.user = user.name
		customer.email_id = user.name
		customer.save(ignore_permissions = True)
		ref = frappe.new_doc("Referral Tree")
		ref.customer = customer.name
		ref.is_group = 1
		ref_no = "Senbagam Paints"
		ref.parent_referral_tree = ref_no
		if args["referral_code"]:
			referral_id=frappe.db.get_value("User", {"referral_id": args["referral_code"]})
			if referral_id:
				customer_doc = frappe.db.get_value("Customer", {"user":referral_id},"name")	
				referral_tree=frappe.get_doc("Referral Tree",customer_doc)
				if referral_tree:
					ref.parent_referral_tree=referral_tree.name
	
			
		
		ref.save(ignore_permissions=True)
		customer.refered_by=referral_tree.name
		customer.save(ignore_permissions=True)
				
		address = frappe.new_doc("Address")
		address.address_title = args["name"]
		address.address_line1 = args["address"]
		address.city = args["city"]
		if args["gstin"]:
			address.gstin = args["gstin"]
			address.gst_category="Registered Regular"
		address.state=args["state"]
		address.district = args["district"]
		address.pincode = args["pincode"]
		address.append('links', {
					"link_doctype": "Customer",
					"link_name": customer.name
					})
		address.save(ignore_permissions = True)
		
		customer.customer_primary_address = address.name
		customer.save(ignore_permissions = True)

		
		frappe.db.commit()
		data["message"] = "Account Created , Please Login"
		return data

	else:
		customer_doc=frappe.get_all("Customer",{"mobile_no":args["mobile_no"]})
		for k in customer_doc:
			cus_doc=frappe.get_doc("Customer",k)
			# cus_doc.refered_by=args["refered_by"]
			cus_doc.user=user.name
			cus_doc.save(ignore_permissions = True)
		frappe.db.commit()
		data["message"] = "Account Created , Please Login"
		return data







@frappe.whitelist(allow_guest=True)
def welcome():
	data = {}
	today= date.today()
	raw = frappe.db.sql("select image as image, content, description from `tabWelcome` where is_active=1 and from_date <= '{0}' and to_date >= '{0}'".format(today), as_dict=True)
	for row in raw:
		if row.image and isinstance(row.image, str) and row.image.startswith('/'):
			image='http://'+frappe.local.request.host+row.image
		

	data["message"] = "Success"
	data["content"] = raw
	return data


@frappe.whitelist(allow_guest=True)
def store():
	data = {}
	raw = frappe.db.sql("select image as image, address, description from `tabStore` where is_active=1 ", as_dict=True)
	data["message"] = "Success"
	data["content"] = raw
	return data


@frappe.whitelist()
def add_quotation(args):
	#   args = loads(args)
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S")

	api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
	user = frappe.db.get_value("User", {"api_key": api_key})
	customer = frappe.db.get_value("Customer", {"user": user})
	doc = frappe.new_doc("Quotation")
	doc.customer = customer
	doc.party_name=customer
	doc.date = date.today()
	for i in args:
		doc.append("items", {
					"item_code": i.strip(),
					"qty": args[i]
					})
	doc.save(ignore_permissions=True)
	return {"message": "Quotation Request Added", "args":args}


@frappe.whitelist()
def get_wallet():
	data = {}
	data["balance"] = 0.0

	api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
	user = frappe.db.get_value("User", {"api_key": api_key})
	customer = frappe.db.get_value("Customer", {"user": user})

	si = frappe.db.sql(""" select name, posting_date as date, CAST(rounded_total as varchar(10)) as amount, CAST(rounded_total * 5 /100 as varchar(10)) as saving  from `tabSales Invoice` where docstatus=1 and customer='{0}' order by creation desc""".format(customer), as_dict=True)
	qt = []
	for i in frappe.db.sql(""" select name from `tabQuotation` where docstatus=1 and party_name='{0}' order by creation desc""".format(customer), as_dict=True):
		doc = frappe.get_doc("Quotation", i.name)
		qt.append({
			"date": doc.transaction_date,
			"name": i.name,
			"amount": str(doc.rounded_total),
			"item": ", ".join([j.item_code for j in doc.items])
				})

	ledger = [
		{
			"date": "YYYY-MM-DD",
			"voucher_no":"Voucher 1",
			"amount": "150",
			"amount_earned": "15",
			"credited_amount": "7",
			"balance": "8"
		},
		{
			"date": "YYYY-MM-DD",
			"voucher_no":"Voucher 2",
			"amount": "300",
			"amount_earned": "30",
			"credited_amount": "20",
			"balance": "10"
		},
		{
			"date": "YYYY-MM-DD",
			"voucher_no": "Voucher 3",
			"amount": "1000",
			"amount_earned": "50",
			"credited_amount": "0",
			"balance": "50"
		},
		{
			"date": "YYYY-MM-DD",
			"voucher_no": "Voucher 4",
			"amount": "5000",
			"amount_earned": "250",
			"credited_amount": "50",
			"balance": "200"
		}
	]

	data["sales_invoice"] = si
	data["quotation"] = qt
	data["ledger"] = ledger
	data["message"] = "Success"
	return data

@frappe.whitelist()
def get_referral_tree():
	api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
	user = frappe.db.get_value("User", {"api_key": api_key})
	customer = frappe.db.get_value("Customer", {"user": user})
	#   customer = "Senbagam Paints"
	tree = get_tree(customer, 1)
	return tree

def get_tree(customer, level):
	if not level <= 2:
		return []
	data = [i.name for i in frappe.db.get_list("Referral Tree", {"parent_referral_tree": customer})]
	ret = {}
	ch = {}
	if level == 1:
		ret["parent"] = [customer]
	ret[customer] = data
	for i in data:
		if i and level != 2:
			ch[i] = get_tree(i, level+1)
			ret = {**ret, **ch[i]}

	return ret

@frappe.whitelist()
def add_bank(args):
	try:
		api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
		user = frappe.db.get_value("User", {"api_key": api_key})
		customer = frappe.db.get_value("Customer", {"user": user})

		doc = frappe.new_doc("Bank Account")
		doc.bank = args["bank_name"]
		doc.party_type = "Customer"
		doc.party = customer
		doc.account_name=args['account_holder_name']
		doc.bank_account_no = args["account_no"]
		doc.ifsc_code = args["ifsc_code"]
		doc.save(ignore_permissions=True)
		return {"message": "Account added Successfully"}
	except:
		return {"message": "Please Try Again"}

@frappe.whitelist()
def get_bank_details():
	api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
	user = frappe.db.get_value("User", {"api_key": api_key})
	customer = frappe.db.get_value("Customer", {"user": user})
	data = frappe.db.sql(""" select bank, account_name as account_holder_name, bank_account_no as account_no, ifsc_code as ifsc_code from `tabBank Account` where party='{0}' order by creation desc limit 1""".format(customer), as_dict=True)
	return {"message": "Success", "data":data}


def get_customer(api_key):
	user = frappe.db.get_value("User", {"api_key": api_key})
	customer = frappe.db.get_value("Customer", {"user": user})
	return customer

@frappe.whitelist()
def add_feedback(args):
	api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
	customer = get_customer(api_key)

	doc= frappe.new_doc("Customer Feedback")
	doc.customer = customer
	doc.feedback = args["feedback"]
	doc.save(ignore_permissions = True)
	return {"message": "Feedback Sent Successfully"}

@frappe.whitelist()
def add_qr(args):
	api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
	customer = get_customer(api_key)

	doc= frappe.new_doc("Scanned QR")
	doc.customer = customer
	doc.qr_code = args["qr_code"]
	doc.save(ignore_permissions = True)
	return {"message": "Reward Claimed"}

@frappe.whitelist()
def get_item():
	data = frappe.db.sql(""" select name as product_type, description from `tabProduct Type` """, as_dict=True)
	items = []
	for i in range(len(data)):
		item = frappe.db.sql(""" select it.name as item_code, it.item_name as item_name,concat('http://', '{0}', it.image) as image, it.show_price as show_price, IFNULL(ip.price_list_rate, 0) as price, false as selected from `tabItem` as it left join `tabItem Price` as ip on it.name=ip.item_code where it.disabled=0 and it.product_type=%s  """.format(frappe.local.request.host), (data[i].product_type), as_dict=1)
		items.append(item)
	return {"section": data, "items":items}




@frappe.whitelist(allow_guest=True)
def dis(state):
    territory=frappe.get_all("Territory",filters={"is_group":0,"parent_territory":state}, pluck="name" ,order_by="name")
    return territory
	
@frappe.whitelist()
def update_profile(args):
	upi_no=False
	error_message = ''
	try:
			# args=json.loads(args)
		api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
		user = frappe.db.get_value("User", {"api_key": api_key})

		user = frappe.get_doc("User", user)
		if user.first_name != args["name"]:
			user.first_name = args["name"]
		if user.birth_date != args["dob"]:
			user.birth_date = args["dob"]

		if user.mobile_no != args["mobile_no"]:
			user.mobile_no = args["mobile_no"]

		user.save(ignore_permissions=True)


		customer = frappe.db.get_value("Customer", {"user": user.name})

		customer = frappe.get_doc("Customer", customer)
		if customer.upi_number:
			upi_no=True

		if customer.customer_name != args["name"]:
			customer.customer_name = args["name"]

		if customer.upi_number != args["upi_no"] or args.get("otp"):
			if args.get("otp") and str(args.get("otp")) == str(customer.custom_upi_otp) and str(args["upi_no"]) == str(customer.custom_unverified_upi_no):
				customer.upi_number = args["upi_no"]
			else:
				error_message = "OTP Verification failed"
				frappe.throw(error_message)

			# frappe.set_value("Customer",{"user": user.name},"docname",args["name"])

		if customer.gstin != args["gstin"]:
			customer.gst_category="Registered Regular"
			customer.gstin = args["gstin"]

		if customer.gstin:
			customer.gst_category="Registered Regular"
		else:
			customer.gst_category="Unregistered"

		customer.save(ignore_permissions=True)



		try:
			address = frappe.get_doc("Address", customer.customer_primary_address)
			if address.address_line1 != args["address"]:
				address.address_line1 = args["address"]

			if address.city != args["city"]:
				address.city = args["city"]

			if address.gstin != args["gstin"]:
				address.gstin = args["gstin"]

			if address.gstin:
				address.gst_category="Registered Regular"
			else:
				address.gst_category="Unregistered"

			if address.state != args.get("state"):
				address.state = args.get("state")

			if address.district != args["district"]:
				address.district = args["district"]

			if address.gst_state != args.get("state"):
				address.gst_state = args.get("state")

			if address.pincode != args["pincode"]:
				address.pincode = args["pincode"]
			address.save(ignore_permissions=True)

		except:
			address=frappe.new_doc("Address")
			address.address_title = args["name"]
			address.address_line1 = args["address"] or ""
			address.city = args["city"] or args["address"]
			address.state = args.get("state")
			address.gst_state = args.get("state")
			address.append('links', {
			"link_doctype": "Customer",
			"link_name": customer.name
			})
			address.save(ignore_permissions=True)
			customer.customer_primary_address = address.name
			customer.save(ignore_permissions=True)

		return {"message": "Profile Updated!","upi_no":upi_no}
	except:
		frappe.local.response.http_status_code = 417
		frappe.local.response['traceback'] = frappe.get_traceback()
		frappe.local.response['error_message'] = error_message
		return {"message": "Please Try Again","upi_no":upi_no, "otp_failed": True if error_message else False}


@frappe.whitelist()
def get_profile():
	api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
	user = frappe.db.get_value("User", {"api_key": api_key})
	user = frappe.get_doc("User", user)
	cust = frappe.db.get_value("Customer", {"user": user.name}, "name")
	customer = frappe.get_doc("Customer", cust)

	address_line1=""
	city=""
	district=""
	pincode =""

	if frappe.db.exists("Address", customer.customer_primary_address):
		address = frappe.get_doc("Address", customer.customer_primary_address)
	else:
		address = frappe._dict()

	if user.user_image:
		if user.user_image.startswith('/'):
			image='https://'+frappe.local.request.host+user.user_image
		else:
			image = user.user_image
	else:
		image=""
	frappe.response["message"] = {
		"message":"Success",
		"name":user.full_name,
		"dob":user.birth_date,
		"mobile_no":user.mobile_no,
		"email":user.email,
		"address": address.address_line1 or "",
		"city":address.city or "",
		"district": address.district or "",
		"state":address.state or "",
		"image_url":image,
		"refered_by":customer.refered_by or "",
		"customer_group":customer.customer_group or "",
		"gstin":customer.gstin or "",
		"pincode":address.pincode or "",
		"upi_no":customer.upi_number or "",
		"roles": [i[0] for i in frappe.db.sql("""SELECT DISTINCT a.role FROM `tabHas Role` as a inner join `tabUser` as b on a.parent = b.name  WHERE a.parent = '{0}'""".format(user.name),as_list=1)]
	}

@frappe.whitelist()
def get_about():
	return {
		"company":frappe.db.get_value("App Settings", "App Settings", "company_name"), 
		"about": frappe.db.get_value("App Settings", "App Settings", "about_us"),
		"account_delete_contact": frappe.db.get_value("App Settings", "App Settings", 'account_deletion_contact')
	}


@frappe.whitelist(allow_guest=True)
def sales_list(args):
	# args=json.loads(args)
	data={}
	result=[]
	balance=frappe.db.sql("""select  sum(loyalty_points) as balance from `tabLoyalty Point Entry` where customer=%s """,(args["customer"]))

	# lastdoc=frappe.get_last_doc("Loyalty Point Entry", {"customer": args["customer"]})
	# if lastdoc:
	a=frappe.get_all("Loyalty Point Entry",filters={"customer":args["customer"]},fields=["customer","invoice","invoiced_customer","loyalty_points"])
	if(a):

		customer0=frappe.get_doc("Customer",a[0]["customer"])
		result.append(a)

		# if customer0.refered_by:

		#     lastdoc1=frappe.get_last_doc("Loyalty Point Entry", {"customer": customer0.refered_by.split("-")[0]})

		#     if lastdoc1:
		#         b=frappe.get_all("Loyalty Point Entry",filters={"name":lastdoc1.name},fields=["customer","invoice","invoiced_customer","loyalty_points"])
		#         customer1=frappe.get_doc("Customer",b[0]["customer"])
		#         result.append(b)
		#         if customer1.refered_by:
		#             lastdoc2=frappe.get_last_doc("Loyalty Point Entry", {"customer": customer1.refered_by.split("-")[0]})
		#             if lastdoc2:
		#                 c=frappe.get_all("Loyalty Point Entry",filters={"name":lastdoc2.name},fields=["customer","invoice","invoiced_customer","loyalty_points"])
		#                 result.append(c)


	if(args["customer"]):
		sales_ord_list = frappe.db.get_all('Sales Order',filters={"customer":args["customer"]})

	#    return sales_ord_list
	for i in sales_ord_list:
		sales_doc = frappe.get_doc('Sales Order',i['name'])
		i.update({
			"status":sales_doc.status,
			"delivery_date":sales_doc.delivery_date,
			"grand_total":sales_doc.grand_total})
		item_list = []
		for item in sales_doc.items:
			item_details = frappe._dict()
			item_details.update({
				"item":item.item_code,
				"item_name":item.item_name,
				"qty":item.qty,
				"amount":item.amount
			})
			item_list.append(item_details)
		i.update({
			"items":item_list
		})

	# a= frappe.db.sql(""" select name,delivery_date,grand_total from `tabSales Order` order by delivery_date asc """, as_dict=True)
	if(args["customer"]):
		sales_inv_list = frappe.db.get_all('Sales Invoice',filters={"customer":args["customer"]})

	for j in sales_inv_list:
		sales_doc = frappe.get_doc('Sales Invoice',j['name'])
		j.update({
			"status":sales_doc.status,
			"posting_date":sales_doc.posting_date,
			"grand_total":sales_doc.grand_total})
		item_list = []
		for item in sales_doc.items:
			item_details = frappe._dict()
			item_details.update({
				"item":item.item_code,
				"item_name":item.item_name,
				"qty":item.qty,
				"amount":item.amount
			})
			item_list.append(item_details)
		j.update({
			"items":item_list
		})


	data["balance"] = balance
	data["loyalty_list"]=a
	data["sales_order"]=sales_ord_list
	data["sales_invoice"]=sales_inv_list

	return data

@frappe.whitelist()
def qr_validate(args):
	# args=json.loads(args)
	if frappe.get_value("Customer",args["customer"],"qr_code_scanned"):
		return "Already QR Scanned."
	original_content=frappe.db.get_all("Company",filters={"qr_content": args["qr_content"]},fields=["qr_content","name"])

		# original_content=frappe.get_value("Company",args["company"],"qr_content")
	if original_content:
		if(original_content[0]["qr_content"] == args["qr_content"]):
			frappe.set_value("Customer",args["customer"],"qr_code_scanned",1)
			frappe.db.commit()
			return "Successfully Verified 🎉"
		else:
			return "Invalid QR"
	else:
		return "Invalid QR"







@frappe.whitelist()
def item_list():
# data = frappe.db.sql(""" select name as section_name, description from `tabProduct Type` """, as_dict=True)

# for i in range(len(data)):
	item = frappe.db.sql(""" select it.name as item_code, it.item_name as item_name, it.image as image from `tabItem` as it where it.disabled=0 """, as_dict=1)

	return { "items":item}


@frappe.whitelist(allow_guest=True)
def company():
	company_dict={}
	data = []
	a= frappe.get_all("Company",fields="name")
	a= sorted(a, key=lambda k: k['name'])
	for i in a:


		filters = [["Dynamic Link", "link_doctype", "=", 'Company'],["Dynamic Link", "link_name", "=", i["name"]],["Dynamic Link", "parenttype", "=", "Address"],]
		Address_list = frappe.get_all("Address", filters=filters, pluck="name")
		try:
			address=frappe.get_value("Address",Address_list[0],"*",as_dict=True) or {}
			file_url=frappe.get_value("File",{"attached_to_doctype":"Company","attached_to_name":i["name"],"attached_to_field":"company_logo"},"file_url") or {}
			image=""
			if file_url:
				if file_url.startswith('/'):
					image='https://'+frappe.local.request.host+file_url
				else:
					image=file_url
			else:
				dafaultimage=frappe.get_doc("Default Store Image")
				if dafaultimage.upload_image:
					if dafaultimage.upload_image.startswith('/'):
						image='https://'+frappe.local.request.host+dafaultimage.upload_image
					else:
						image=dafaultimage.upload_image
						
			address.update({"image":image})
			address.update({"company":i["name"]})
			data.append(address)
			company_dict["content"]=data
		except:
			address={}
			file_url=frappe.get_value("File",{"attached_to_doctype":"Company","attached_to_name":i["name"],"attached_to_field":"company_logo"},"file_url") or {}
			image=""
			if file_url:
				if file_url.startswith('/'):
					image='https://'+frappe.local.request.host+file_url
				else:
					image=file_url

			else:
				dafaultimage=frappe.get_doc("Default Store Image")
				if dafaultimage.upload_image:
					if dafaultimage.upload_image.startswith('/'):
						image='https://'+frappe.local.request.host+dafaultimage.upload_image
					else:
						image=dafaultimage.upload_image
			address.update({"image":image})
			address.update({"company":i["name"]})
			data.append(address)
			company_dict["content"]=data


	return company_dict


@frappe.whitelist(allow_guest=True)
def state():
	state=frappe.get_meta("Address").fields
	s=""
	for i in state:
		if i.fieldname=="gst_state":
			s=i.options
			break
	if s:
		f=s.split("\n")
	else:
		f=[]
	f=[i for i in f if i]
	frappe.local.response["message"]=f


@frappe.whitelist(allow_guest=True)
def loyalty_list(args):
	# args=json.loads(args)
	data={}
	result=[]
	lastdoc=frappe.get_last_doc("Loyalty Point Entry", {"customer": args["customer"]})

	a=frappe.get_all("Loyalty Point Entry",filters={"name":lastdoc.name},fields=["customer","invoice","invoiced_customer","loyalty_points"])

	customer0=frappe.get_doc("Customer",a[0]["customer"])
	result.append(a)
	if customer0.refered_by:

		lastdoc1=frappe.get_last_doc("Loyalty Point Entry", {"customer": customer0.refered_by.split("-")[0]})

		if lastdoc1:
			b=frappe.get_all("Loyalty Point Entry",filters={"name":lastdoc1.name},fields=["customer","invoice","invoiced_customer","loyalty_points"])
			customer1=frappe.get_doc("Customer",b[0]["customer"])
			result.append(b)
			if customer1.refered_by:
				lastdoc2=frappe.get_last_doc("Loyalty Point Entry", {"customer": customer1.refered_by.split("-")[0]})
				if lastdoc2:
					c=frappe.get_all("Loyalty Point Entry",filters={"name":lastdoc2.name},fields=["customer","invoice","invoiced_customer","loyalty_points"])
					result.append(c)
	data["loyalty_list"]=result
	return data


@frappe.whitelist(allow_guest=True)
def otpgen(args):   
	if args.get("no_validate") or frappe.get_doc("User", {"mobile_no": args["mobile_no"]}):
		otp=""
		for i in range(4):
			otp+=str(r.randint(1,9))

		if args.get("customer"):
			frappe.db.set_value("Customer", args["customer"], "custom_unverified_upi_no", args["mobile_no"])
			frappe.db.set_value("Customer", args["customer"], "custom_upi_otp", otp)

		url = f"""https://control.msg91.com/api/v5/otp?template_id=6564463ed6fc056e4804c023&mobile=91{args["mobile_no"]}&authkey=387408ATKT6CcDJGRW63aa76cbP1&otp={otp}"""
		payload = {}
		headers = {
		'Cookie': 'PHPSESSID=sqs84cvd082o57gnt6judbd2k6'
		}
		requests.request("GET", url, headers=headers, data=payload)

		return {"message":"OTP sent successfully","otp":otp}
	else:
		frappe.local.response.http_status_code = 417

		return {"message":"The number you have entered is not registered.","otp":""}


# @frappe.whitelist(allow_guest=True)
# def getitem():
#     data = frappe.get_all("Item",fields=["distinct item_group"])
# #    data = frappe.db.sql(""" select name as item_group_name, description from `tabItem Group` """, as_dict=True)

#     items = []
#     for i in range(len(data)):
#         item = frappe.db.sql(""" select it.name as item_code, it.item_name as item_name,concat('http://', '{0}', it.image) as image, it.show_price as show_price, IFNULL(ip.price_list_rate, 0) as price, false as selected from `tabItem` as it left join `tabItem Price` as ip on it.name=ip.item_code where it.disabled=0 and it.item_group=%s """.format(frappe.local.request.host), (data[i].item_group), as_dict=1)
#         items.append(item)
#     return {"section": data, "items":items}

# @frappe.whitelist(allow_guest=True)
# def getitem():
#     data = frappe.get_all("Item",fields=["distinct item_group"])
#     items=[]

#     for i in range(len(data)):
#         items1 = []
#         items2 = []
#         item = frappe.db.sql(""" select it.name as item_code, it.item_name as item_name,concat('http://', '{0}', it.image) as image, it.show_price as show_price,it.app_priority , IFNULL(ip.price_list_rate, 0) as price, false as selected from `tabItem` as it left join `tabItem Price` as ip on it.name=ip.item_code where it.disabled=0 and it.item_group=%s and ip.price_list="Standard Selling"  order by it.app_priority asc,ip.valid_from desc""".format(frappe.local.request.host), (data[i].item_group), as_dict=1)
#         for j in item:
#             if j["app_priority"]!=0:
#                 items1.append(j)
#             else:
#                 items2.append(j)
#         items.append(items1 + items2)
#     return {"section": data, "items":items}


@frappe.whitelist(allow_guest=True)
def getitem():
	# data = frappe.get_all("Item",fields=["distinct item_group"])
	items=[]
	dict1={"item_group":"Products"}
	data=[]
	data.append(dict1)
	# for i in range(len(data)):
	items1 = []
	items2 = []
	item = frappe.db.sql(""" select it.name as item_code, it.item_name as item_name,concat('http://', '{0}', it.image) as image, it.show_price as show_price,it.app_priority , IFNULL(ip.price_list_rate, 0) as price, false as selected from `tabItem` as it left join `tabItem Price` as ip on it.name=ip.item_code where it.disabled=0 and it.item_group="Products" and ip.price_list="Store Sales Rate Standard Selling"  order by it.app_priority asc,ip.valid_from desc""".format(frappe.local.request.host), as_dict=1)
	for j in item:
		if j["app_priority"]!=0:
			items1.append(j)
		else:
			items2.append(j)
	items.append(items1 + items2)
	return {"section": data, "items":items}

@frappe.whitelist()
def bank_list():
	namelist=[]
	banklist=frappe.get_all("Bank")
	for i in banklist:
		namelist.append(i['name'])

	return namelist


@frappe.whitelist(allow_guest=True)
def update_bank_details(args):

	try:
		bank = frappe.get_doc("Bank Account", {'party':args['customer']})

		if bank.bank != args["bank_name"]:
			bank.bank = args["bank_name"]

		if bank.account_name != args["account_holder_name"]:
			bank.account_name = args["account_holder_name"]
		if bank.bank_account_no != args["account_no"]:
			bank.bank_account_no = args["account_no"]
		if bank.ifsc_code != args["ifsc_code"]:
			bank.ifsc_code = args["ifsc_code"]
		bank.save(ignore_permissions=True)

		return {"message": "Bank Details Updated!"}
	except:
		return {"message":"Please Try Again"}







# @frappe.whitelist(allow_guest=True)
# def test():
#     company_dict={}
#     data = []
#     a= frappe.get_all("Company",fields="name")
#     a= sorted(a, key=lambda k: k['name'])
#     for i in a:


#         filters = [["Dynamic Link", "link_doctype", "=", 'Company'],["Dynamic Link", "link_name", "=", i["name"]],["Dynamic Link", "parenttype", "=", "Address"],]
#         Address_list = frappe.get_all("Address", filters=filters, pluck="name")
#         try:
#             address=frappe.get_value("Address",Address_list[0],"*",as_dict=True) or {}
#             file_url=frappe.get_value("File",{"attached_to_doctype":"Company","attached_to_name":i["name"],"attached_to_field":"company_logo"},"file_url") or {}
#             image='https://'+frappe.local.request.host+file_url
#             address.update({"image":image})
#             address.update({"company":i["name"]})
#             data.append(address)
#             company_dict["content"]=data
#         except:
#             address={}
#             file_url=frappe.get_value("File",{"attached_to_doctype":"Company","attached_to_name":i["name"],"attached_to_field":"company_logo"},"file_url") or {}
#             if file_url:
#                 image='https://'+frappe.local.request.host+file_url
#             else:
#                 dafaultimage=frappe.get_doc("Default Store Image")
#                 image='https://'+frappe.local.request.host+dafaultimage.upload_image
#             address.update({"image":image})
#             address.update({"company":i["name"]})
#             data.append(address)
#             company_dict["content"]=data


#     return company_dict


@frappe.whitelist(allow_guest=True)
def get_referral_name(id = None):
	if id:
		id = frappe.db.get_value("User", {"referral_id": id}, "name")
	
	id = id or 'Senbagam Paints'
	return id

@frappe.whitelist()
def get_user_referral_id(user):
	id = frappe.db.get_value("User", user, "referral_id")
	if not id:
		while (id:=frappe.generate_hash(user, 10)) and frappe.db.get_value("User", {"referral_id": id}, "name"):
			pass
		frappe.db.set_value("User", user, "referral_id", id)

	links = frappe.db.get_value("App Settings", "App Settings", ["android_app_link", "ios_app_link"], as_dict=True)
	frappe.local.response["android_app_link"] = links.android_app_link or ''
	frappe.local.response["ios_app_link"] = links.ios_app_link or ''
	return id



@frappe.whitelist()
def delete_account():
	api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
	user = frappe.db.get_value("User", {"api_key": api_key},"name")
	user_doc=frappe.get_doc("User",user)
	user_doc.enabled=1
	user_doc.save(ignore_permissions=True)
	return {"message": "Account deleted Successfully"}