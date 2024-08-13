import frappe
import datetime
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils import add_days, cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate
from erpnext.setup.doctype.company.company import update_company_current_month_sales
from erpnext.accounts.doctype.sales_invoice.sales_invoice import update_linked_doc
from erpnext.accounts.doctype.sales_invoice.sales_invoice import check_if_return_invoice_linked_with_payment_entry
from erpnext.accounts.doctype.sales_invoice.sales_invoice import unlink_inter_company_doc
from erpnext.stock.doctype.serial_no.serial_no import (
	get_delivery_note_serial_no,
	get_serial_nos,
	update_serial_nos_after_submit,
)


class Custom_Sales_Invoice(SalesInvoice):
	def on_submit(self):
		
		self.validate_pos_paid_amount()

		if not self.auto_repeat:
			frappe.get_doc("Authorization Control").validate_approving_authority(
				self.doctype, self.company, self.base_grand_total, self
			)

		self.check_prev_docstatus()

		if self.is_return and not self.update_billed_amount_in_sales_order:
			# NOTE status updating bypassed for is_return
			self.status_updater = []

		self.update_status_updater_args()
		self.update_prevdoc_status()
		self.update_billing_status_in_dn()
		self.clear_unallocated_mode_of_payments()

		# Updating stock ledger should always be called after updating prevdoc status,
		# because updating reserved qty in bin depends upon updated delivered qty in SO
		if self.update_stock == 1:
			self.update_stock_ledger()
		if self.is_return and self.update_stock:
			update_serial_nos_after_submit(self, "items")

		# this sequence because outstanding may get -ve
		self.make_gl_entries()

		if self.update_stock == 1:
			self.repost_future_sle_and_gle()

		if not self.is_return:
			self.update_billing_status_for_zero_amount_refdoc("Delivery Note")
			self.update_billing_status_for_zero_amount_refdoc("Sales Order")
			self.check_credit_limit()

		self.update_serial_no()

		if not cint(self.is_pos) == 1 and not self.is_return:
			self.update_against_document_in_jv()

		self.update_time_sheet(self.name)

		if (
			frappe.db.get_single_value("Selling Settings", "sales_update_frequency") == "Each Transaction"
		):
			update_company_current_month_sales(self.company)
			self.update_project()
		update_linked_doc(self.doctype, self.name, self.inter_company_invoice_reference)

		# create the loyalty point ledger entry if the customer is enrolled in any loyalty program
		if not self.is_return and not self.is_consolidated and self.loyalty_program:
			pass
			# self.make_loyalty_point_entry()
		elif (
			self.is_return and self.return_against and not self.is_consolidated and self.loyalty_program
		):
			against_si_doc = frappe.get_doc("Sales Invoice", self.return_against)
			against_si_doc.delete_loyalty_point_entry()
			# against_si_doc.make_loyalty_point_entry()
		if self.redeem_loyalty_points and not self.is_consolidated and self.loyalty_points:
			self.apply_loyalty_points()

		self.process_common_party_accounting()

	def on_cancel(self):
			check_if_return_invoice_linked_with_payment_entry(self)

			super(SalesInvoice, self).on_cancel()

			self.check_sales_order_on_hold_or_close("sales_order")

			if self.is_return and not self.update_billed_amount_in_sales_order:
				# NOTE status updating bypassed for is_return
				self.status_updater = []

			self.update_status_updater_args()
			self.update_prevdoc_status()
			self.update_billing_status_in_dn()

			if not self.is_return:
				self.update_billing_status_for_zero_amount_refdoc("Delivery Note")
				self.update_billing_status_for_zero_amount_refdoc("Sales Order")
				self.update_serial_no(in_cancel=True)

			# Updating stock ledger should always be called after updating prevdoc status,
			# because updating reserved qty in bin depends upon updated delivered qty in SO
			if self.update_stock == 1:
				self.update_stock_ledger()

			self.make_gl_entries_on_cancel()

			if self.update_stock == 1:
				self.repost_future_sle_and_gle()

			self.db_set("status", "Cancelled")

			if (
				frappe.db.get_single_value("Selling Settings", "sales_update_frequency") == "Each Transaction"
			):
				update_company_current_month_sales(self.company)
				self.update_project()
			if not self.is_return and not self.is_consolidated and self.loyalty_program:
				self.delete_loyalty_point_entry()
			elif (
				self.is_return and self.return_against and not self.is_consolidated and self.loyalty_program
			):
				against_si_doc = frappe.get_doc("Sales Invoice", self.return_against)
				against_si_doc.delete_loyalty_point_entry()
				# against_si_doc.make_loyalty_point_entry()

			unlink_inter_company_doc(self.doctype, self.name, self.inter_company_invoice_reference)

			self.unlink_sales_invoice_from_timesheets()
			self.ignore_linked_doctypes = (
				"GL Entry",
				"Stock Ledger Entry",
				"Repost Item Valuation",
				"Payment Ledger Entry",
			)

def loyalty_points(self,event):
	if self.status == "Paid":
		customer =frappe.get_doc("Customer",self.customer)
		
		if customer.refered_by:
			refered_customer =frappe.get_doc("Customer",customer.refered_by)
			loyalty_points=self.net_totaltotal*4/100
			create_doc=frappe.new_doc("Loyalty Point Entry")
			create_doc.customer=refered_customer.name
			create_doc.invoiced_customer=self.customer
			create_doc.invoice_type=self.doctype
			create_doc.invoice=self.name
			create_doc.loyalty_points= loyalty_points
			create_doc.purchase_amount=self.net_totaltotal
			create_doc.posting_date=self.posting_date
			create_doc.company=self.company
			create_doc.save(ignore_permissions=True)
			if refered_customer.refered_by:
				refered_customer1 =frappe.get_doc("Customer",refered_customer.refered_by)
				loyalty_points=self.net_totaltotal*2/100
				create_doc=frappe.new_doc("Loyalty Point Entry")
				create_doc.customer=refered_customer1.name
				create_doc.invoiced_customer=self.customer
				create_doc.invoice_type=self.doctype
				create_doc.invoice=self.name
				create_doc.loyalty_points= loyalty_points
				create_doc.purchase_amount=self.net_total
				create_doc.posting_date=self.posting_date
				create_doc.company=self.company
				create_doc.save(ignore_permissions=True)

			




		

