frappe.ui.form.on('Company', {
    
	qr_content: function(frm) {
       
		frm.set_df_property("qr", "options", '<img src="https://barcode.tec-it.com/barcode.ashx?data={{ frm.doc.qr_content }}&code=QRCode">');
		frm.refresh();
		
	},
	refresh: function(frm) {
        
		frm.set_df_property("qr", "options", '<img src="https://barcode.tec-it.com/barcode.ashx?data={{ frm.doc.qr_content }}&code=QRCode">');
		
		
	}
});
