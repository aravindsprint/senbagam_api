import frappe
from frappe.model.naming import parse_naming_series

def naming_series(self,event):
    if self.is_return :
        self.name=parse_naming_series(f'SR{self.city_abbr}{self.abbr}-.YYYY.-.####')  
    else:
    
        self.name=parse_naming_series(f'SI{self.city_abbr}{self.abbr}-.YYYY.-.####')  