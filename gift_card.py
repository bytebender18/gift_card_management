from flask import Flask, jsonify, request
import psycopg2
import jwt
from datetime import datetime

app = Flask(__name__)
con = psycopg2.connect(host='localhost',database='postgres',user='',password='')
cursor = con.cursor()


@app.route('/api/register', methods =['POST'])
def user_registration():
	try:
		data = request.json 
		username = data['username']
		password = data['password']
		email = data['email']

		insert_query = """Insert into account(username, password, email) values (%s,%s,%s)"""
		cursor.execute(insert_query,(username,password,email))
		con.commit()

		return jsonify({"message":"User created successfully", "status_code":"201"}), 201

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/login', methods =['PUT'])
def user_login():
	try:
		data = request.json 
		username = data['username']
		password = data['password']

		select_query = """select * from account where username = '{}'""".format(username)
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()
		email = select_cursor[0][3]
				

		if username == select_cursor[0][1]:
			if password == select_cursor[0][2]:
				update_query = """update account set is_active= %s where email= %s"""
				cursor.execute(update_query,(True,email))
				con.commit()
				return jsonify({"message":"Login successful", "status_code":"200"}), 200

			else:
				return jsonify({"message":"User does not exist."})

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/logout', methods=['POST'])
def user_logout():
	try:
		data = request.json 
		username = data['username']
		password = data['password']

		select_query = """select * from account where username = '{}'""".format(username)
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()
		email = select_cursor[0][3]
				

		if username == select_cursor[0][1]:
			if password == select_cursor[0][2]:
				update_query = """update account set is_active= %s where email= %s"""
				cursor.execute(update_query,(False,email))
				con.commit()
				return jsonify({"message":"Logout successful", "status_code":"200"}), 200

			else:
				return jsonify({"message":"User does not exist."})


	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/cards', methods=['POST'])
def add_card():
	try:
		data = request.json 
		card_number = data['card_number']
		expiration_date = data['expiration_date']
		cvv = data['cvv']
		pin = data['pin']
		amount = data['amount']
		account_id = data['account_id']

		converted_date = datetime.strptime(expiration_date, "%m/%y").strftime("%d-%m-%y")

		if not account_exists(account_id):
			return jsonify({"message":"Account doesn't exist"}), 404

		insert_query = """Insert into cards(card_number,expiration_date,cvv,pin,amount,account_id) values (%s,%s,%s,%s,%s,%s)"""
		cursor.execute(insert_query,(card_number,converted_date,cvv,pin,amount,account_id))
		con.commit()

		return jsonify({"message":"Card added successfully", "status_code":"201"}), 201


	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/balance', methods=['GET'])
def balance_inquiry():
	try:
		data = request.json
		card_number = data['card_number']
		pin = data['pin']

		select_query = """select * from cards where card_number = '{}'""".format(card_number)
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()

		if not len(select_cursor)>0:
			return jsonify({"message":"Incorrect card number entered"}),401

		if card_number == select_cursor[0][1]:

			if pin == select_cursor[0][4]:
				amount = select_cursor[0][5]
				return jsonify({"message":"Balance inquiry successful","balance":amount,"status_code":"200"}),200
			else:
				return jsonify({"message":"Incorrect PIN entered"}),401

		else:		
			return jsonify({"message":"Incorrect card number entered"}),401


	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/withdraw', methods=['PUT'])
def balance_withdrawal():
	try:
		data = request.json
		card_number = data['card_number']
		pin = data['pin']
		amount = data['amount']
		formatted_string = float(amount)

		select_query = """select * from cards where card_number = '{}'""".format(card_number)
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()
		actual_amount = select_cursor[0][5]

		if formatted_string>actual_amount:
			return jsonify({"message":"Insufficient balance"}),400

		new_balance = actual_amount - formatted_string

		update_query = """update cards set amount = %s where card_number = %s"""
		cursor.execute(update_query,(new_balance,card_number))
		con.commit()

		return jsonify({"message":"Withdrawal successful","status_code":"200"}),200

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/cards/<int:account_id>', methods=['GET'])
def get_all_cards(account_id):
	try:	
		if not account_exists(account_id):
			return jsonify({"message":"Account doesn't exist"}), 404

		select_query = """select * from cards where account_id = '{}'""".format(account_id)
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()

		response = []
		for info in select_cursor:
			x = {"card_number":hide_card_number(info[1]),"expiration_date":get_expiry_date_in_MMYY(info[2])}
			response.append(x)

		return jsonify({"cards":response}),200

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


def account_exists(account_id):
	select_query = """select * from account where id = '{}' """.format(account_id)
	cursor.execute(select_query)
	select_cursor = cursor.fetchall()

	if len(select_cursor)>0:
		return True
	else:
		return False


def hide_card_number(card_number):
	return "*"*12 + card_number[-4:]


def get_expiry_date_in_MMYY(exp_date):
	return exp_date.strftime("%m/%y")



if __name__ == '__main__':
	app.run(port=8080,debug=True)






