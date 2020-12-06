def excepthook(type, value, tb):
	import traceback
	traceback.print_exception(type, value, tb)
	input()
import sys
sys.excepthook = excepthook

from requests import get
from csv import DictReader
from os import chdir
from os.path import isfile, join as pathJoin
from docx import Document
from re import compile
from tempfile import gettempdir

temp_dir = gettempdir()

# chdir(temp_dir)

def get_csv(url):
	filename = pathJoin(temp_dir, url[url.rfind("/")+1:])
	if not isfile(filename):
		print("downloading " + url)
		file_csv = get(url)
		print(str(len(file_csv.text)) + " downloaded to " + filename)
		open(filename, "wt").write(file_csv.text)
	return DictReader(open(filename, "rt"))

def get_laws():
	return get_csv("https://production.oknesset.org/pipelines/data/bills/kns_bill/kns_bill.csv")

def get_docs():
	return get_csv("https://production.oknesset.org/pipelines/data/bills/kns_documentbill/kns_documentbill.csv")
	
def get_doc(url):
	filename = pathJoin(temp_dir, url[url.rfind("/")+1:])
	if(not isfile(filename)):
		print("downloading from " + url + " to " + filename)
		data = get(url)
		#print(str(len(data.text)) + " downloaded from " + url + " to " + filename)
		#data.raw.decode_content = True
		open(filename, "wb").write(data.content)
	return Document(filename)
	
laws = {}
for law in get_laws():
	laws[law["BillID"]] = law

print(str(len(laws)) + " laws loaded")

dups=compile("(פ/[0-9]+/2(1|3|2))")
init = compile("יוז(מות|מים|מת|ם):\t? +חבר(ות|י|ת)? הכנסת\t")

scored_laws = {}
for name in ["laws21", "laws22"]:
	dict = DictReader(open(name+ ".csv", "rt"))
	for line in dict:
		if line.get("מספר חוק") and line.get("ניקוד לחוק") != None:
			scored_laws[line["מספר חוק"]] = line

scores = [['"שם הצעת החוק","מדרג","מספר חוק",ניקוד", "קישור להצעת החוק", "הסבר הדירוג","הערות אחרות","הגיע להצבעה?","עבר?","יוזם ראשון","חתומים"']] + [[]] * 3000
n = 1
for line in DictReader(open("laws23" + ".csv", "rt")):
	if not line.get("מספר חוק"):
		line["מספר חוק"] = ("פ/" + str(n) + "/23")
	if line.get("הסבר הדירוג").find("ראה חוק") > 0 and not line.get("מדרג") :
		line["מדרג"] = "dup_laws_bot"
	scores[int(line.get("מספר חוק")[int(line.get("מספר חוק").find("/"))+1:int(line.get("מספר חוק").rfind("/"))])] = [
		"\"" + line.get("שם הצעת החוק") + "\"", line.get("מדרג"), line.get("מספר חוק"),
		line.get("ניקוד לחוק"),line.get("קישור להצעה"),"\""+line.get("הסבר הדירוג").replace("\"", "'")+"\"",
		line.get("הערות אחרות"),line.get("הגיע להצבעה?"),line.get("עבר?"),line.get("יוזם ראשון"),line.get("חתומים")]
	n+=1
	if line.get("ניקוד לחוק") != None:
		if line.get("מספר חוק"):
			scored_laws[line["מספר חוק"]] = line

duplicates = {}
laws_initiators = [[]]*3000

news_csv = 'קישור, שם, מספר\n'
unscored_csv = 'קישור, שם, מספר, עלה להצבעה\n'
old_csv = 'קישור, שם, מספר חדש, דירוג, מספר קודם\n'

i = 0
for doc in get_docs():
	i += 1
	# if i%1000 == 0:
	# 	print(i)

	law = laws.get(doc["BillID"])
	if not law:
		print("law " + str(doc["BillID"]) + " not found")
		# print(doc)
		continue


	if law["KnessetNum"] != '23':
		continue

	# 53 - הצעה ממשלתית
	# 54 - הצעה פרטית
	# 55 - ועדה
	if law["SubTypeID"] != '54':
		if law["SubTypeID"] not in ["53", "54", "55"]:
			print(law["SubTypeID"], law["SubTypeDesc"])
		continue
	
	# 1 - דיון מוקדם
	# 2 - הצעת חוק לקריאה הראשונה
	# 4 - הצעת חוק לקריאה השנייה והשלישית
	# 5 - הצעת חוק לקריאה השנייה והשלישית - לוח תיקונים
	# 8 - חוק - נוסח לא רשמי
	# 9 - חוק - פרסום ברשומות
	# 17 - החלטת ממשלה
	# 46 - הצעת חוק לקריאה השנייה והשלישית - הנחה מחדש
	# 51 - הצעת חוק לדיון מוקדם - נוסח מתוקן
	# 101 - הצעת חוק לקריאה השניה והשלישית - פונצ  בננה
	# 102 - הצעת חוק לקריאה השניה והשלישית - לוח תיקונים - פונצ בננה
	# 103 - הצעת חוק לקריאה השנייה והשלישית - הנחה מחדש- פונצ בננה
	if doc["GroupTypeID"] != '1':
		if doc["GroupTypeID"] not in ['51', "1", "2", "4", "5", "8", "9", "17", "46", "101", "102", "103",]:
			print(doc["GroupTypeID"], doc["GroupTypeDesc"])
		continue
	
	num = int(law["PrivateNumber"])
	law_name = "פ\\23\\{}".format(num)
	if not scores[num]:
		scores[num] = ["\"" + law["Name"].replace("\"", "'") + "\""] + [''] * 8
	if not scores[num][2]:
		scores[num][2] = law_name
	if not scores[num][4]:
		scores[num][4] = 'https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawBill.aspx?t=lawsuggestionssearch&lawitemid=' + law["BillID"]
	# print(law)
	if law["StatusID"] in ["104", "141"]:
		scores[num][7] = "0"
		scores[num][8] = "0"
	elif law["StatusID"] == "118":
		# חוק עבר
		scores[num][7] = "1"
		scores[num][8] = "1"
	elif law["StatusID"] == "177":
		if(law["PostponementReasonID"] in ["3013", "3012", "3011", "3010", "1065", "2511"]):
			# נדחה בגלל שהח"כ המציע עזב את הכנסת
			scores[num][7] = "0"
			scores[num][8] = "0"
		else:
			# נדחה בהצבעה
			scores[num][7] = "1"
			scores[num][8] = "0"
	else:
		scores[num][7] = "1"
		scores[num][8] = "0"

	old_names = None
	#print(doc["GroupTypeDesc"], doc["FilePath"])
	for p in get_doc(doc["FilePath"]).paragraphs:
		if init.match(p.text): #.find("יוזמים:      חברי הכנסת") == 0:
			initiators = [a.strip() for a in init.sub("", p.text).replace("_", "").split("\n")]
			initiators = [a for a in initiators if a]
			laws_initiators[num] = initiators
			scores[num][9:] = initiators

		other_names = [i[0] for i in dups.findall(p.text)]
		if p.text.find("חוק") > 0 and other_names and (p.text.find("זהות")>=0 or p.text.find("זהה")>=0):
			old_names = other_names
			for name in old_names:
				if scored_laws.get(name):
					if scored_laws[name]["שם הצעת החוק"].find(law['Name'][10:20]) == -1:
							print("כפילות בשם שונה!", law['Name'], law_name, scored_laws[name]["שם הצעת החוק"], name)
					if duplicates.get(law_name):
						#print("law scored already twice! " + str(scored_laws[name]) + str(duplicates[law_name]))
						if scored_laws[name]["ניקוד לחוק"] != duplicates[law_name]["ניקוד לחוק"]:
							print("חוק דורג פעמיים בעבר בניקוד שונה", law["Name"], scored_laws[name]["ניקוד לחוק"], scored_laws[name]["מספר חוק"], duplicates[law_name]["ניקוד לחוק"], duplicates[law_name]["מספר חוק"])
					duplicates[law_name] = scored_laws[name]
					old_csv += ('https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawBill.aspx?t=lawsuggestionssearch&lawitemid=' + law["BillID"] + ",\"" + law['Name'].replace("\"", "'") + "\"," + law_name + "," + scored_laws[name]["ניקוד לחוק"] + "," + scored_laws[name]["מספר חוק"] + "\n")
					if not scores[int(law_name[5:])][3] and scored_laws[name]["ניקוד לחוק"] != "":
						scores[int(law_name[5:])][1:6] = ["dup_laws_bot", law_name, 
							scored_laws[name]["ניקוד לחוק"],'https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawBill.aspx?t=lawsuggestionssearch&lawitemid=' + law["BillID"],
							"\"" + (scored_laws[name]["הסבר הדירוג"] + " ראה חוק\n" + scored_laws[name]["מספר חוק"] + " " + scored_laws[name]["קישור להצעה"]).replace("\"", "'") + "\""]

	if not old_names:
		news_csv += ('https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawBill.aspx?t=lawsuggestionssearch&lawitemid=' + law["BillID"] + ",\"" + law['Name'].replace("\"", "'") + "\"," + law_name + "\n")
		if scored_laws.get(name) == None and scores[num][3] == "":
			unscored_csv += ('https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawBill.aspx?t=lawsuggestionssearch&lawitemid=' + law["BillID"] + ",\"" + law['Name'].replace("\"", "'") + "\"," + law_name + "," + scores[num][7] + "\n")
	if not scores[num][9]:
		print("no iniitiators", [p.text for p in get_doc(doc["FilePath"]).paragraphs])
open("unscored_laws.csv", "wt").write(unscored_csv)
open("new_laws.csv", "wt").write(news_csv)
open("scored_laws.csv", "wt").write(old_csv)
open("table.csv", "wt").write("\n".join([",".join(line) for line in scores]))
open("initiators.csv", "wt").write("\n".join([",".join(line) for line in laws_initiators]))