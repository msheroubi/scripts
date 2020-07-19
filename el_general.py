from connect import Connect
from pymongo import MongoClient
import psycopg2
from dateutil.parser import parse

def establishConnection():
	try:
		conn=psycopg2.connect(dbname= '<db_name>', host='<host_url>', port= '<port>', user= '<user>', password= '<password>')
		print("Connection Successful.")
		return conn
	except:
		print("Failed to connect to host.")
		conn.close()
		return -1

def commitChanges():
	try:
		conn.commit()
		print("Changes Committed.")
	except:
		print("Could not commit changes.")
def makeQuery(sql):
	try:
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchall()
		return data
	except:
		print("Could not execute query or fetch results.")
		return -1
	finally:
		cur.close()

def updateQuery(sql):
	try:
		cur = conn.cursor()
		cur.execute(sql)
		return 1
	except:
		print("Could not execute update.")
		return -1
	finally:
		cur.close()	

def closeConnection():
	try:
		conn.close()
		print("Connection Closed.")
	except:
		print("Could not close connection.")

def matchType(type_in, value):
	if type_in is str:
		if is_date(value):
			return "DATE"
		else:
			return "VARCHAR(100)"
	elif type_in is bool:
		return "BOOLEAN"
	elif type_in is int:
		return "INT"
	elif type_in is float:
		return "DECIMAL(9,2)"

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


# table_name here is just the table_name (e.g. campaign) / (schema_name is mongocapstone, etltest, etc..)
check_col = """SELECT *
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = '{schema_name}' AND TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{col_name}' """


# table_name here is the schema_name.table_name (e.g. etltest.campaign)
add_col = """ALTER TABLE {table_name} 
ADD {col_name} {data_type} NULL;"""

insert_query = """ INSERT INTO {table_name}({attributes}) VALUES ({values}); """

createTable_query = """CREATE TABLE {schema_name}.{table_name} ( _id VARCHAR(100) ); """

schema_name = "etltest"

try:
	conn = establishConnection() #Redshift

	client = Connect.get_connection() #MongoDb
	db =  client['test']	

	## Add any other mongo collections here // Rename existing collections
	# collections = ['organization', 'campaign', 'user', 'checkout', 'tickets']
	collections = ['organization']

	# Initialize Tables
	for ele in collections:
		sql = createTable_query.format(schema_name=schema_name, table_name=ele)
		print("Creating Table - " + ele)
		print(sql)
		updateQuery(sql)
	commitChanges()

	for ele in collections:
		table_name = schema_name + '.' + ele
		col = db[ele] 		#Collections listed must exist in mongo instance
		query = {}			#'Select *'
		doc = col.find(query)

		checked_columns = []
		### First Run - Check that all attributes exist, if not, add to relation
		for row in doc:
			for attr in row:
				value = row[attr]
				data_type = matchType(type(value), value)

				if attr not in checked_columns:
					sql = check_col.format(schema_name=schema_name, table_name=ele, col_name=attr)
					print("Checking for Column: " + attr)
					rst = makeQuery(sql)

					if rst != -1 and rst == []:			#If query is executed, but returns 0 rows
						sql = add_col.format(table_name=table_name, col_name=attr, data_type=data_type)
						print("Inserting new Column: " + attr)
						updateQuery(sql)

					checked_columns.append(attr)
					commitChanges()

		doc = col.find(query)
		### Second Run - Insert All Values 
		for row in doc:
			attributes = ''
			values = []
			for attr in row:
				attributes+= (attr) +','
				values.append(row[attr])
			attributes = attributes[:-1]
			sql = insert_query.format(table_name=table_name, attributes=attributes, values=values)
			sql = sql.replace('[', '')
			sql = sql.replace(']', '')
			print("Inserting DOCUMENT into  " + table_name)
			updateQuery(sql)
			commitChanges()

except Exception as e:
	print(e)
finally:
	commitChanges()
	closeConnection()
