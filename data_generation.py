from faker import Faker
from faker.providers import internet, profile, date_time, lorem
import random

cypher_node_file = open("cypher_node_data.cql", "w")
cypher_rel_file = open("cypher_rel_data.cql", "w")
sql_file = open("sql_data.sql", "w")

def closeFiles():
	cypher_node_file.close()
	cypher_rel_file.close()
	sql_file.close()

def generateUserData(n):
	fake = Faker()
	fake.add_provider(profile)
	fake.add_provider(date_time)

	for i in range(1,n+1):
		#fake.simple_profile() creates a fake user profile, including username, name, address, email
		temp_profile = fake.simple_profile(sex=None)

		#adress from profile includes both street and city, so we split them
		temp_address, temp_city = temp_profile['address'].split('\n')
		temp_city = temp_city.split(',')
		temp_city = temp_city[0]

		#temp_date = fake.date_this_decade(before_today=True, after_today=False)
		temp_date = fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None)

		sql_node_user = "INSERT INTO Users(user_id, user_name, name, address, city, email, created_at) VALUES ({},\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\');".format(i,temp_profile['username'],temp_profile['name'], temp_address, temp_city, temp_profile['mail'], temp_date)
		cypher_node_user = "CREATE (n:User {{user_id:{},user_name:'{}', name:'{}', address:'{}', city:'{}', email:'{}', created_at:'{}'}});".format(i,temp_profile['username'],temp_profile['name'], temp_address, temp_city, temp_profile['mail'], temp_date)
		
		sql_file.write(sql_node_user + "\n")
		# print(sql_node_user)
		cypher_node_file.write(cypher_node_user + "\n")
		# print(cypher_node_user)

def generateGroupData(n, x=25):
	common_nouns = open('common-nouns.txt').read().splitlines()
	group_suffix = ['Group', 'Fans', 'Team', 'Group']
	fake = Faker()
	fake.add_provider(date_time)
	fake.add_provider(lorem)

	for i in range(1,n+1):
		temp_date = fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None)
		temp_description = fake.paragraph(nb_sentences=random.randint(3,6), variable_nb_sentences=True, ext_word_list=None)
		temp_group_name = random.choice(common_nouns).capitalize() + " " + random.choice(common_nouns).capitalize() + " " + random.choice(group_suffix)
		temp_user =  random.randint(1, x)

		sql_node_group = "INSERT INTO Groups(group_id, user_id, group_name, description, created_at) VALUES ({}, {}, \'{}\', \'{}\', \'{}\');".format(i, temp_user,temp_group_name, temp_description, temp_date)
		cypher_node_group = "CREATE (n:Group {{group_id:{}, group_name:'{}', description:'{}', created_at:'{}'}});".format(i,temp_group_name, temp_description,temp_date)
		cypher_rel_creates = "MATCH (u:User),(g:Group) WHERE u.user_id = {} AND g.group_id = {} CREATE (u)-[r:creates {{created_at:'{}'}}]->(g);".format(temp_user, i, temp_date)


		sql_file.write(sql_node_group + "\n")
		cypher_node_file.write(cypher_node_group+ "\n")
		cypher_rel_file.write(cypher_rel_creates + "\n")
		# print(sql_node_group)
		# print(cypher_node_group)
		# print(cypher_rel_creates)
		# print("\n")

def generateInterestData(n):
	# common_interests = open('common-interests.txt').read().splitlines()
	for i in range(1, n+1):
		# x = random.randint(0,len(common_interests)-1)
		# interest = common_interests[x]
		# common_interests.pop(x)			#Dont allow duplicates
		interest = 'interest{}'.format(i)

		sql_node_interest = "INSERT INTO Interests(interest_id, interest_name) VALUES ({}, \'{}\');".format(i, interest)
		cypher_node_interest = "CREATE (n:Interest {{interest_id:{}, interest_name:'{}'}});".format(i, interest)


		sql_file.write(sql_node_interest + "\n")
		cypher_node_file.write(cypher_node_interest+ "\n")
		# print(sql_node_interest)
		# print(cypher_node_interest)
		# print("\n")

def generateEventData(n, x=25, y=5):
	common_interests = open('common-interests.txt').read().splitlines()
	common_verbs = open('common-verbs.txt').read().splitlines()
	fake = Faker()
	fake.add_provider(date_time)
	fake.add_provider(lorem)
	fake.add_provider(profile)

	for i in range(1,n+1):
		temp_date = fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None)
		temp_start_date = fake.date_time_between_dates(datetime_start=temp_date, datetime_end=None)
		temp_end_date = fake.date_time_between_dates(datetime_start=temp_start_date, datetime_end=None)
		temp_description = fake.paragraph(nb_sentences=random.randint(2,4), variable_nb_sentences=True, ext_word_list=None)

		temp_profile = fake.simple_profile(sex=None)
		#adress from profile includes both street and city, so we split them
		temp_address, temp_city = temp_profile['address'].split('\n')
		temp_city = temp_city.split(',')
		temp_city = temp_city[0]

		verbing = random.choice(common_verbs).capitalize()
		if verbing[-1:]=='e':
			verbing= verbing[:-1] + "ing"
		else:
			verbing= verbing + 'ing'

		#Create an event name: A combination between an interest and a verb ending in ING
		temp_event_name = random.choice(common_interests) + " " + verbing

		cypher_node_event = "CREATE (n:Event {{event_id:{}, event_name:'{}', description:'{}', created_at:'{}', event_start:'{}', event_end:'{}', address:'{}', city:'{}'}});".format(i, temp_event_name, temp_description, temp_date, temp_start_date, temp_end_date, temp_address, temp_city)
		#If event is hosed by a user or a group
		coin = random.randint(0,1)
		if coin == 0:
			temp_user = random.randint(1, x)

			sql_node_event = "INSERT INTO Events(event_id, user_id, event_name, description, created_at, event_start, event_end, address, city) VALUES ({}, {}, \'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\');".format(i, temp_user ,temp_event_name, temp_description, temp_date, temp_start_date, temp_end_date, temp_address, temp_city)
			cypher_rel_creates = "MATCH (u:User),(e:Event) WHERE u.user_id = {} AND e.event_id = {} CREATE (u)-[r:creates {{created_at:'{}'}}]->(e);".format(temp_user, i, temp_date)
		else:
			temp_group = random.randint(1, y)
			sql_node_event = "INSERT INTO Events(event_id, group_id, event_name, description, created_at, event_start, event_end, address, city) VALUES ({}, {}, \'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\');".format(i, temp_group, temp_event_name, temp_description, temp_date, temp_start_date, temp_end_date, temp_address, temp_city)
			cypher_rel_creates = "MATCH (g:Group),(e:Event) WHERE g.group_id = {} AND e.event_id = {} CREATE (g)-[r:creates {{created_at:'{}'}}]->(e);".format(temp_group, i, temp_date)

		#Write to file
		sql_file.write(sql_node_event + "\n")
		cypher_node_file.write(cypher_node_event+ "\n")
		cypher_rel_file.write(cypher_rel_creates + "\n")
		# print(sql_node_event)
		# print(cypher_node_event)
		# print(cypher_rel_creates)
		# print("\n")

def generatePostData(n, x=25,y=5, z=5):
	fake = Faker()
	fake.add_provider(date_time)
	fake.add_provider(lorem)

	for i in range(1,n+1):
		temp_date = fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None)
		temp_content = fake.paragraph(nb_sentences=random.randint(3,6), variable_nb_sentences=True, ext_word_list=None)
		temp_user = random.randint(1, x)

		#Create two relationships for posts, first relationship is between user and post, User =[Creates]> Post
		#Second relationship is between either group and post, or event and post, where a group [has]> post, or event [has]> post
		cypher_node_post = "CREATE (n:Post {{post_id:{}, content:'{}', created_at:'{}'}});".format(i, temp_content, temp_date)
		cypher_rel_creates = "MATCH (u:User),(p:Post) WHERE u.user_id = {} AND p.post_id = {} CREATE (u)-[r:creates {{created_at:'{}'}}]->(p);".format(temp_user, i, temp_date)
		#If post is in a group or an event page
		coin = random.randint(0,1)

		if coin==0:	
			temp_event = random.randint(1,z)

			sql_node_post = "INSERT INTO Posts(post_id, user_id, event_id, content, created_at) VALUES ({}, {}, {}, \'{}\', \'{}\');".format(i, temp_user, temp_event, temp_content, temp_date)
			cypher_rel_has = "MATCH (e:Event),(p:Post) WHERE e.event_id = {} AND p.post_id = {} CREATE (e)-[r:has]->(p);".format(temp_event, i)
		else:
			temp_group = random.randint(1,y)

			sql_node_post = "INSERT INTO Posts(post_id, user_id, group_id, content, created_at) VALUES ({}, {}, {}, \'{}\', \'{}\');".format(i, temp_user, temp_group, temp_content, temp_date)
			cypher_rel_has = "MATCH (g:Group),(p:Post) WHERE g.group_id = {} AND p.post_id = {} CREATE (g)-[r:has]->(p);".format(temp_group, i)

		#Write to file
		sql_file.write(sql_node_post + "\n")
		cypher_node_file.write(cypher_node_post+ "\n")
		cypher_rel_file.write(cypher_rel_creates + "\n")
		cypher_rel_file.write(cypher_rel_has + "\n")
		# print(sql_node_post)
		# print(cypher_node_post)
		# print(cypher_rel_creates)
		# print(cypher_rel_has)
		# print("\n")

def generateIsMemberData(n,x=25,y=5):
	fake = Faker()
	fake.add_provider(date_time)
	existing_combos = [[]]
	for i in range(1, n+1):
		temp_date = fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None)

		temp_user = random.randint(1,x)
		temp_group = random.randint(1,y)

		while([temp_user, temp_group] in existing_combos):
			temp_user = random.randint(1,x)
			temp_group = random.randint(1,y)
		existing_combos.append([temp_user, temp_group])

		sql_rel_isMember = "INSERT INTO isMember(user_id, group_id, member_since) VALUES ({},{},\'{}\');".format(temp_user, temp_group, temp_date)
		cypher_rel_isMember = "MATCH (u:User),(g:Group) WHERE u.user_id = {} AND g.group_id = {} CREATE (u)-[r:isMember {{member_since:\'{}\'}}]->(g);".format(temp_user, temp_group, temp_date)

		#Write to file
		sql_file.write(sql_rel_isMember + "\n")
		cypher_rel_file.write(cypher_rel_isMember + "\n")
		# print(sql_rel_isMember)
		# print(cypher_rel_isMember)
		# print("\n")

def generateIsAttendingData(n, x=25, y=5):
	existing_combos = [[]]
	for i in range(1, n+1):
		temp_user = random.randint(1,x)
		temp_event = random.randint(1,y)

		while([temp_user, temp_event] in existing_combos):
			temp_user = random.randint(1,x)
			temp_event = random.randint(1,y)
		existing_combos.append([temp_user, temp_event])
		sql_rel_isAttending = "INSERT INTO isAttending(user_id, event_id) VALUES ({},{});".format(temp_user, temp_event)
		cypher_rel_isAttending = "MATCH (u:User),(e:Event) WHERE u.user_id = {} AND e.event_id = {} CREATE (u)-[r:isAttending]->(e);".format(temp_user, temp_event)

		#Write to file
		sql_file.write(sql_rel_isAttending + "\n")
		cypher_rel_file.write(cypher_rel_isAttending + "\n")
		# print(sql_rel_isAttending)
		# print(cypher_rel_isAttending)
		# print("\n")

def generateSendsMessageData(n, x=25):
	fake = Faker()
	fake.add_provider(lorem)

	for i in range(1, n+1):
		temp_user1 = random.randint(1,x)
		temp_user2 = random.randint(1,x)

		while(temp_user1 == temp_user2):
			temp_user2 = random.randint(1,x)

		temp_message= fake.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None)
		sql_node_message = "INSERT INTO sendsMessage(message_id, sender_id, recipient_id, content) VALUES ({},{},{},\'{}\');".format(i, temp_user1, temp_user2, temp_message)
		cypher_rel_sendsMessage = "MATCH (u:User),(v:User) WHERE u.user_id = {} AND v.user_id = {} CREATE (u)-[r:sendsMessage {{content:'{}'}}]->(v);".format(temp_user1, temp_user2, temp_message)

		#Write to file
		sql_file.write(sql_node_message + "\n")
		cypher_rel_file.write(cypher_rel_sendsMessage + "\n")
		# print(sql_node_message)
		# print(cypher_rel_sendsMessage)
		# print("\n")

def generateIsFriendsWithData(n, x=25):
	fake = Faker()
	fake.add_provider(date_time)
	existing_combos = [[]]
	for i in range(1, n+1):
		temp_user1 = random.randint(1,x)
		temp_user2 = random.randint(1,x)

		while([temp_user1, temp_user2] in existing_combos):
			temp_user1 = random.randint(1,x)
			temp_user2 = random.randint(1,x)
		existing_combos.append([temp_user1, temp_user2])

		temp_date = fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None)
		sql_rel_isFriendsWith = "INSERT INTO isFriendsWith(user_id, friend_id, created_at) VALUES ({},{},\'{}\');".format(temp_user1, temp_user2, temp_date)
		cypher_rel_isFriendsWith = "MATCH (u:User),(v:User) WHERE u.user_id = {} AND v.user_id = {} CREATE (u)-[r:isFriendsWith {{created_at:'{}'}}]->(v);".format(temp_user1, temp_user2, temp_date)

		#Write to file
		sql_file.write(sql_rel_isFriendsWith + "\n")
		cypher_rel_file.write(cypher_rel_isFriendsWith + "\n")
		# print(sql_rel_isFriendsWith)
		# print(cypher_rel_isFriendsWith)
		# print("\n")

def generateLeavesCommentData(n, x=25, y=5):
	fake = Faker()
	fake.add_provider(date_time)
	fake.add_provider(lorem)

	for i in range(1, n+1):
		temp_user = random.randint(1,x)
		temp_post = random.randint(1,y)

		temp_comment= fake.paragraph(nb_sentences=random.randint(1,5), variable_nb_sentences=True, ext_word_list=None)
		temp_date = fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None)

		#Comment's primnary key is both its own comment id and a post id, the comment id is an identity so it doesn't need to be idenified here.
		sql_node_comment = "INSERT INTO leavesComment(comment_id, post_id, user_id, content, created_at) VALUES ({},{},{},\'{}\', \'{}\');".format(i, temp_post, temp_user, temp_comment, temp_date)
		#Comments don't need indices in Neo4j
		cypher_rel_leavesComment = "MATCH (u:User),(p:Post) WHERE u.user_id = {} AND p.post_id = {} CREATE (u)-[r:leavesComment {{content:'{}', created_at:'{}'}}]->(p);".format(temp_user, temp_post, temp_comment, temp_date)

		#Write to file
		sql_file.write(sql_node_comment + "\n")
		cypher_rel_file.write(cypher_rel_leavesComment + "\n")
		# print(sql_node_comment)
		# print(cypher_rel_leavesComment)
		# print("\n")

def generateHasInterestData(n, m, x=25, y=5, z=5):
	fake = Faker()
	fake.add_provider(date_time)
	existing_combos = [[]]

	for i in range(1, n+1):
		coin = random.randint(1,6)

		temp_interest = random.randint(1,m)

		temp_user = random.randint(1,x)
		temp_group = random.randint(1,y)
		temp_event = random.randint(1,z)

		temp_date = fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None)
		temp_degree = random.randint(1,10)

		##Interest-Interest Relationships
		if coin == 1:
			temp_interest2 = random.randint(1,m)
			while(temp_interest==temp_interest2):
				temp_interest2 = random.randint(1,m)

			combo = [coin, temp_interest, temp_interest2]
			while(combo in existing_combos):
				temp_interest2 = random.randint(1,m)
				combo = [coin, temp_interest, temp_interest2]

			existing_combos.append(combo)
			sql_rel_hasInterest = "INSERT INTO Interest_to_Interest(interest_id, related_interest_id, degree) VALUES ({}, {}, {});".format(temp_interest, temp_interest2, temp_degree)
			cypher_rel_hasInterest = "MATCH (j:Interest),(i:Interest) WHERE j.interest_id = {} AND i.interest_id = {} CREATE (j)-[r:hasInterest {{degree:'{}'}}]->(i);".format(temp_interest, temp_interest2, temp_degree)
		elif coin == 2: #Group Interest
			combo = [coin, temp_interest, temp_group]
			while(combo in existing_combos):
				temp_group = random.randint(1,y)
				combo = [coin, temp_interest, temp_group]

			existing_combos.append(combo)
			sql_rel_hasInterest = "INSERT INTO Group_to_Interest(group_id, interest_id) VALUES ({}, {});".format(temp_group, temp_interest)
			cypher_rel_hasInterest = "MATCH (g:Group),(i:Interest) WHERE g.group_id = {} AND i.interest_id = {} CREATE (g)-[r:hasInterest]->(i);".format(temp_group, temp_interest)
		elif coin == 3:			#Event Interests
			combo = [coin, temp_interest, temp_event]
			while(combo in existing_combos):
				temp_event = random.randint(1,z)
				combo = [coin, temp_interest, temp_event]

			existing_combos.append(combo)
			sql_rel_hasInterest = "INSERT INTO Event_to_Interest(event_id, interest_id) VALUES ({}, {});".format(temp_event, temp_interest)
			cypher_rel_hasInterest = "MATCH (e:Event),(i:Interest) WHERE e.event_id = {} AND i.interest_id = {} CREATE (e)-[r:hasInterest]->(i);".format(temp_event, temp_interest)
		else:		#User Interest
			combo = [temp_interest, temp_user]
			while(combo in existing_combos):
				temp_user = random.randint(1,x)
				combo = [temp_interest, temp_user]

			existing_combos.append(combo)
			sql_rel_hasInterest = "INSERT INTO User_to_Interest(user_id, interest_id, created_at) VALUES ({}, {}, \'{}\');".format(temp_user, temp_interest, temp_date)
			cypher_rel_hasInterest = "MATCH (u:User),(i:Interest) WHERE u.user_id = {} AND i.interest_id = {} CREATE (u)-[r:hasInterest {{created_at:'{}'}}]->(i);".format(temp_user, temp_interest, temp_date)

		#Write to file
		sql_file.write(sql_rel_hasInterest + "\n")
		cypher_rel_file.write(cypher_rel_hasInterest + "\n")
		# print(sql_rel_hasInterest)
		# print(cypher_rel_hasInterest)
		# print("\n")
def generateData(n):
	num_users = n // 20
	num_groups = n // 100
	num_interests = n // 50
	# if num_interests > 473:
	# 	num_interests = 473
	num_events = n // 50
	num_posts = n // 10
	num_members = n // 10
	num_friends = n // 10
	num_comments = (n // 20) + (n // 10)
	num_hasInterests = n // 5
	num_attending = n // 10
	num_messages = (n // 20) + (n // 10)

	print("Users: {} | Groups: {} | Interests: {} | Events: {} | Posts: {} | isMember: {} | areFriends: {} | comments: {} | hasInterest: {} | isAttending: {} | messages: {} |".format(num_users, num_groups, num_interests, num_events, num_posts, num_members, num_friends, num_comments, num_hasInterests, num_attending, num_messages))
	generateUserData(num_users)
	generateGroupData(num_groups, num_users)
	generateInterestData(num_interests)
	generateEventData(num_events, num_users, num_groups)
	generatePostData(num_posts, num_users, num_groups, num_events)
	generateIsMemberData(num_members, num_users, num_groups)
	generateIsAttendingData(num_attending, num_users, num_events)
	generateSendsMessageData(num_messages, num_users)
	generateIsFriendsWithData(num_friends, num_users)
	generateLeavesCommentData(num_comments, num_users, num_posts)
	generateHasInterestData(num_hasInterests, num_interests, num_users, num_groups, num_events)
	closeFiles()

def generateAllData(num_users, num_groups, num_interests, num_events, num_posts, num_members, num_friends, num_comments, num_hasInterests, num_attending, num_messages):
	# cypher_node_file = open("cypher_node_data.cql", "w+")
	# cypher_rel_file = open("cypher_rel_data.cql", "w+")
	# sql_file = open("sql_data.sql", "w+")

	generateUserData(num_users)
	generateGroupData(num_groups, num_users)
	generateInterestData(num_interests)
	generateEventData(num_events, num_users, num_groups)
	generatePostData(num_posts, num_users, num_groups, num_events)
	generateIsMemberData(num_members, num_users, num_groups)
	generateIsAttendingData(num_attending, num_users, num_events)
	generateSendsMessageData(num_messages, num_users)
	generateIsFriendsWithData(num_friends, num_users)
	generateLeavesCommentData(num_comments, num_users, num_posts)
	generateHasInterestData(num_hasInterests, num_interests, num_users, num_groups, num_events)

# try:
# 	# num_users = 25
# 	# num_groups = 5
# 	# num_interests = 10
# 	# num_events = 10
# 	# num_posts = 50
# 	# num_members = 50
# 	# num_friends = 50
# 	# num_comments = 75
# 	# num_hasInterests = 100
# 	# num_attending = 50
# 	# num_messages = 75
# 	# generateAllData(num_users, num_groups, num_interests, num_events, num_posts, num_members, num_friends, num_comments, num_hasInterests, num_attending, num_messages)

# 	sizes = [5000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000]
# 	generateData(5000)
# except Exception as e:
# 	print(e)

# generateData(100000)