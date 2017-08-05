from lxml import html, etree
import sqlite3
import requests
import sys
import os

RESULTS_LENGTH_STRING = "?resultsperpage=100"
filename = "freecycleupdate.html"

def runQuery(queryString):
	cur.execute(queryString)
	return cur.fetchall()
	
def getPageHTML(url):
	get_success = False
	for i in range(3):
		try:	
			page = requests.get(url)
		except requests.exceptions.ConnectionError:
			continue	# Try again or exit loop
		get_success = True
		break

	if not get_success:
		return -1

	html_tree = html.fromstring(page.content)
	return html_tree
	
def boolToInt(bool):
	if bool == True:
		return 1
	else:
		return 0

def linkExists(link):
	count = len(runQuery("SELECT * FROM posts WHERE link='" + link + "'"))
	if count == 0:
		return False
	else:
		return True
		
# Widen : ?resultsperpage=100
urls = sys.argv[1:]

# Setup memory-based database
con = sqlite3.connect("freecycle.sqlite")
cur = con.cursor()
cur.execute("CREATE TABLE if not exists posts( \
				id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
				timestamp INTEGER, \
				title TEXT NOT NULL, \
				location TEXT NOT NULL, \
				sublocation TEXT NOT NULL, \
				link TEXT NOT NULL, \
				new BOOLEAN);")
		
for url in urls:
	page_data = getPageHTML(url + RESULTS_LENGTH_STRING)
	if page_data == -1:
		print("Unable to connect to " + url)
		exit(-1)

	# Parse page
	table = page_data.xpath('//*[@id="group_posts_table"]/tr')
	post_location = page_data.xpath('//*[@id="content"]/h2/a')[0].text_content()
	for row in table:
		post_timestamp = 0
		post_title = "N/A"
		post_sublocation = "N/A"
		post_link = "N/A"
		post_new = True
		first_td = True
		for data in row:	# 2 td for each tr
			for subdata in data:	
				if (subdata.tag == "a") and (first_td == False):
					post_link = subdata.get("href")
					if post_title == "N/A":
						post_title = subdata.text_content()
			if first_td == False:
				sublocation_unfiltered = data.text_content()
				post_sublocation = sublocation_unfiltered[sublocation_unfiltered.find("(")+1:sublocation_unfiltered.find(")")].strip()		# Not ideal. Finds lots of data then just filters to match whichever if the first between ( and ).
			first_td = False
		if linkExists(post_link):
			update_command = "UPDATE posts SET new = '0' WHERE link='" + post_link + "'"
			cur.execute(update_command)
		else:
			insertion_command = "INSERT INTO posts (timestamp, title, location, sublocation, link, new) VALUES (" + str(post_timestamp).replace("'", "''") + ", '" + post_title.replace("'", "''") + "', '" + post_location.replace("'", "''") + "', '" + post_sublocation.replace("'", "''") + "', '" + post_link + "', " + str(boolToInt(post_new)) + ");"
			cur.execute(insertion_command)
		
# Write table to file

#column_names = [name[1] for name in runQuery("PRAGMA table_info(posts)")]
#for name in column_names:
	#print(name)
#	pass

result = runQuery("SELECT title, location, sublocation, link, new FROM posts ORDER BY new DESC")
rows = list()
for row in result:
	dataElements = list()
	for dataElement in row:
		dataElements.append("<td>" + str(dataElement) + "</td>")
	if dataElements[-1] == "<td>1</td>":	# Bad, code better
		rows.append("<tr bgcolor=\"#008000\">" + str("".join(dataElements[:-1])) + "</tr>")
	else:
		rows.append("<tr bgcolor=\"#FF0000\">" + str("".join(dataElements[:-1])) + "</tr>")
	
xmlTable = "<table border=\"1\" cellpadding=\"3\" style=\"white-space:nowrap;border-collapse:collapse;>\"" + str("".join(rows)) + "</table>"
with open(filename, "w") as html_file:
    html_file.write(xmlTable)

con.commit()

os.system("start "+ filename)
