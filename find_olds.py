from requests import get
from csv import DictReader
from os import chdir
from os.path import isfile
from docx import Document
from re import compile

temp_dir = 'C:\\Users\\ohad\\AppData\\Local\\Temp\\'

chdir(temp_dir)

def get_csv(url):
	filename = temp_dir + url[url.rfind("/")+1:]
	if isfile(filename):
		return DictReader(open(filename, "rt"))
	print("downloading " + url)
	file_csv = get(url)
	print(str(len(file_csv.text)) + " downloaded to " + filename)
	open(filename, "wt").write(file_csv.text)
	return DictReader(file_csv.text)

def get_laws():
	return get_csv("https://production.oknesset.org/pipelines/data/bills/kns_bill/kns_bill.csv")

def get_docs():
	return get_csv("https://production.oknesset.org/pipelines/data/bills/kns_documentbill/kns_documentbill.csv")
	
def get_doc(url):
	filename = temp_dir + url[url.rfind("/")+1:]
	if(not isfile(filename)):
		#print("downloading from " + url + " to " + filename)
		data = get(url)
		#print(str(len(data.text)) + " downloaded from " + url + " to " + filename)
		#data.raw.decode_content = True
		open(filename, "wb").write(data.content)
	return Document(filename)
	
laws = {}
for law in get_laws():
	laws[law["BillID"]] = law

print(str(len(laws)) + " laws loaded")

dups=compile("פ/[0-9]+/22")

scored_laws = {}
for name in ["laws21", "laws22"]:
	dict = DictReader(open(name+ ".csv", "rt"))
	for line in dict:
		if line.get("מספר חוק") and line.get("ניקוד לחוק"):
			scored_laws[line["מספר חוק"]] = line

scores = [['"ניקוד"', '"קישור להצעת החוק"', '"הסבר הדירוג"']] + [['']*3]*3000
for line  in DictReader(open("laws23" + ".csv", "rt")):
		if line.get("מספר חוק") and line.get("ניקוד לחוק"):
			scored_laws[line["מספר חוק"]] = line
			scores[int(line.get("מספר חוק")[int(line.get("מספר חוק").find("/"))+1:int(line.get("מספר חוק").rfind("/"))])] = [line.get("ניקוד לחוק"),line.get("קישור להצעה"),"\""+line.get("הסבר הדירוג").replace("\"", "'")+"\""]

duplicates = {}
news = []

news_csv = 'קישור, שם, מספר\n'
unscored_csv = 'קישור, שם, מספר\n'
old_csv = 'קישור, שם, מספר חדש, דירוג, מספר קודם\n'

i = 0
kns = [0]*24
for doc in get_docs():
	i += 1
	#if i%1000 == 0:
	#	print(i)
	#if not laws.get(doc["BillID"]):
	#	print(doc["BillID"])
	#	continue
	law = laws.get(doc["BillID"])
	kns[int(law["KnessetNum"])] += 1
	if law["KnessetNum"] != '23':
		#print(law["KnessetNum"])		
		continue
	if law["SubTypeID"] != '54':
		#print(law["SubTypeDesc"], law["SubTypeID"])
		continue
	if doc["GroupTypeID"] != '1':
		#print(doc["GroupTypeID"], doc["GroupTypeDesc"])
		continue
	#print(doc["GroupTypeDesc"], doc["FilePath"])
	for p in get_doc(doc["FilePath"]).paragraphs:
		if p.text.find("חוק") > 0 and (p.text.find("/22") > 0 or p.text.find("/23") > 0 or p.text.find("/21") > 0) and (p.text.find("זהות")>0 or p.text.find("זהה")>0):
			law_name = "פ\\23\\{}".format(law["PrivateNumber"])
			old_names = dups.findall(p.text)
			if not old_names:
				news_csv += ('https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawBill.aspx?t=lawsuggestionssearch&lawitemid=' + law["BillID"] + ",\"" + law['Name'].replace("\"", "'") + "\"," + law_name + "\n")
			for name in old_names:
				if scored_laws.get(name):
					if scored_laws[name]["שם הצעת החוק"][:scored_laws[name]["שם הצעת החוק"].rfind(",")] != \
						law['Name'][:law['Name'].rfind(",")]:
							print("כפילות בשם שונה!", law['Name'], law_name, scored_laws[name]["שם הצעת החוק"], name)
					if duplicates.get(law_name):
						#print("law scored already twice! " + str(scored_laws[name]) + str(duplicates[law_name]))
						if scored_laws[name]["ניקוד לחוק"] != duplicates[law_name]["ניקוד לחוק"]:
							print("חוק דורג פעמיים בעבר בניקוד שונה", law["Name"], scored_laws[name]["ניקוד לחוק"], scored_laws[name]["מספר חוק"], duplicates[law_name]["ניקוד לחוק"], duplicates[law_name]["מספר חוק"])
					duplicates[law_name] = scored_laws[name]
					old_csv += ('https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawBill.aspx?t=lawsuggestionssearch&lawitemid=' + law["BillID"] + ",\"" + law['Name'].replace("\"", "'") + "\"," + law_name + "," + scored_laws[name]["ניקוד לחוק"] + "," + scored_laws[name]["מספר חוק"] + "\n")
					if not scores[int(law_name[5:])][1]:
						scores[int(law_name[5:])] = [#"\"" + law['Name'] + "\"", "old_laws_bot", law_name, 
							scored_laws[name]["ניקוד לחוק"],'https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawBill.aspx?t=lawsuggestionssearch&lawitemid=' + law["BillID"],
							"\"" + (scored_laws[name]["הסבר הדירוג"] + " ראה חוק " + scored_laws[name]["מספר חוק"] + " " + scored_laws[name]["קישור להצעה"]).replace("\"", "'") + "\""]
			if not duplicates.get(law_name):
				news.append(law)
				unscored_csv += ('https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawBill.aspx?t=lawsuggestionssearch&lawitemid=' + law["BillID"] + ",\"" + law['Name'].replace("\"", "'") + "\"," + law_name + "\n")
open("unscored_laws.csv", "wt").write(unscored_csv)
open("new_laws.csv", "wt").write(news_csv)
open("scored_laws.csv", "wt").write(old_csv)
open("table.csv", "wt").write("\n".join([",".join(line) for line in scores]))