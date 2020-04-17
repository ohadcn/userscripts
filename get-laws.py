from knesset_data.dataservice.bills import Bill
from datetime import datetime
from os import path
from json import load, dump
# ['DEFAULT_ORDER_BY_FIELD', 'DEFAULT_REQUEST_TIMEOUT_SECONDS', 'METHOD_NAME', 'ORDERED_FIELDS', 'SERVICE_NAME', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_entry', '_fields', '_get_all_pages', '_get_instance_from_entry', '_get_method_name', '_get_request_exception', '_get_response_content', '_get_service_name', '_get_soup', '_get_url_base', '_get_url_page', '_get_url_single', '_handle_prop', '_parse_entry', '_parse_entry_data', '_parse_entry_id', '_parse_entry_links', '_proxies', '_session', '_set_field_value', 'all_field_values', 'all_schema_field_values', 'committee_id', 'error_report', 'get', 'get_all', 'get_field', 'get_fields', 'get_json_table_schema', 'get_page', 'id', 'is_continuation', 'kns_num', 'last_update', 'magazine_num', 'name', 'num', 'page_num', 'postponent_reason_desc', 'postponent_reason_id', 'private_num', 'public_date', 'public_series_desc', 'public_series_first_call', 'public_series_id', 'status_id', 'sum_law', 'type_description', 'type_id']

# OrderedDict([('id', 17791), ('kns_num', 16), ('name', 'הצעת חוק הגנת הפרטיות (תיקון - איסור פרסום בדבר עבר מיני של נפגע עבירת מין או אלימות), התשס"ד-2003'), ('type_id', 54), ('type_description', 'פרטית'), ('private_num', 1568), ('committee_id', None), ('status_id', 104), ('num', None), ('postponent_reason_id', None), ('postponent_reason_desc', None), ('public_date', None), ('magazine_num', None), ('page_num', None), ('is_continuation', None), ('sum_law', None), ('public_series_id', None), ('public_series_desc', None), ('public_series_first_call', None), ('last_update', datetime.datetime(2013, 5, 23, 18, 37, 57))])

# OrderedDict([('id', 5), ('kns_num', 1), ('name', 'חוק שכר חברי הכנסת, התש"ט-1949'), ('type_id', 53), ('type_description', 'ממשלתית'), ('private_num', None), ('committee_id', 377), ('status_id', 118), ('num', None), ('postponent_reason_id', None), ('postponent_reason_desc', None), ('public_date', datetime.datetime(1949, 6, 7, 0, 0)), ('magazine_num', 10), ('page_num', 41), ('is_continuation', None), ('sum_law', None), ('public_series_id', 6071), ('public_series_desc', 6071), ('public_series_first_call', None), ('last_update', datetime.datetime(2016, 3, 8, 11, 1, 1))])

# OrderedDict([('id', 20), ('kns_num', 7), ('name', 'חוק מקצועות רפואיים (אגרות), התשל"א-1971'), ('type_id', 53), ('type_description', 'ממשלתית'), ('private_num', None), ('committee_id', 280), ('status_id', 118), ('num', 887), ('postponent_reason_id', None), ('postponent_reason_desc', None), ('public_date', datetime.datetime(1971, 4, 7, 0, 0)), ('magazine_num', 618), ('page_num', 68), ('is_continuation', None), ('sum_law', None), ('public_series_id', 6071), ('public_series_desc', 6071), ('public_series_first_call', None), ('last_update', datetime.datetime(2016, 3, 8, 11, 0, 56))])
# {'הסרה מסד"י בד. מוקדם': 2505, 'הסרה מסד"י בהמלצת ועדה אחרי ק-1': 2508, 'חזרת הח"כ המציע לפני ד. מוקדם': 2511, 'לא נתקבלה בק-3': 2510, 'הח"כ המציע מונה לשר/סגן שר': 3013, 'לא הושג הרוב הדרוש': 3112, 'הסרה מסד"י בהמלצת ועדה אחרי ד. מוקדם': 2506, 'חזרת הח"כ המציע אחרי ד. מוקדם': 2512, 'לא נתקבלה בק-1': 2507, 'לא הושג הרוב הדרוש - הצ"ח תקציבית': 3086, 'הח"כ המציע התפטר': 3012, 'הח"כ המציע נפטר': 3011, 'לא נתקבלה בק-2': 2509, 'מונה לנשיא': 3010, 'חזרת הממשלה מהצעת החוק': 1065, 'הצעת החוק לא נדונה/לא הוצבעה במועד': 3087}

start = datetime.now()
p23 = []
laws23=[]
i=0
storeme = None
datafilename = "laws.data"
if(path.isfile(datafilename)):
	bills = load(open(datafilename, "rb"))
else:
	bills = Bill.get_all()
	storeme = []
for bill in bills:
	if(storeme != None):
		bill = bill.all_field_values()
		storeme.append(bill)
	if(i%1000 == 0):
		print(i)
	i+=1
	if(bill["kns_num"] == 23):
		laws23.append(bill)
		if(bill["type_id"]==54):
			stat = bill["status_id"]
			status = []
			if(stat in [104, 141]):
				status.append(0)
			elif(stat == 177):
				if(bill["postponent_reason_id"] in [3013, 3012, 3011, 3010, 1065, 2511]):
					status.append(0)
				else:
					status.append(1)
			else:
				status.append(1)
			
			if(stat in [118]):
				status.append(1)
			else:
				status.append(0)

			if(len(p23) < bill["private_num"]+1):
				p23.extend((bill["private_num"]+1-len(p23))*[[0, 0, 0, 0, 0]])
			status.append(bill["name"])
			status.append("https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawBill.aspx?t=lawsuggestionssearch&lawitemid=" + str(bill["id"]))
			status.append(bill["postponent_reason_desc"])
			p23[bill["private_num"]] = status
			
open("file.csv", "wt").write("\n".join(["{},{},{},{},{}".format(*law) for law in p23]))
if(storeme != None):
	dump([{key:o[key] for key in o.keys() if type(o[key]) != datetime} for o in storeme], open(datafilename, "wb"))
print(datetime.now() - start)

