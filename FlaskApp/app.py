from flask import Flask, render_template, json, request
from flask.ext.mysql import MySQL
from selenium import webdriver
from Crypto.Cipher import XOR
import time, base64
# from werkzeug import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)
secret = 'SNAP@rochester'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'developer'
app.config['MYSQL_DATABASE_PASSWORD'] = 'developer'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

'''
This function checks of a webbrowser can login to gmail
using the email and passwd provided by the participant
Returns True if successful, else False
'''
def verify_gmail_login(email, passwd):
	login_status = False
	gmail_url = "https://accounts.google.com/Login#identifier"
	driver = webdriver.PhantomJS()
	driver.set_window_size(1120, 550)
	driver.get(gmail_url)
	time.sleep(1)
	driver.find_element_by_id('Email').send_keys(email)
	driver.find_element_by_id("next").click()
	time.sleep(1)
	driver.find_element_by_id('Passwd').send_keys(passwd)
	driver.find_element_by_id("signIn").click()
	time.sleep(2)
	current_url = driver.current_url
	if 'https://myaccount.google.com' in current_url:
		login_status = True
		print '***Logged in successfully!!!****'
	driver.quit()
	return login_status


def encrypt(key, plaintext):
  cipher = XOR.new(key)
  return base64.b64encode(cipher.encrypt(plaintext))

def decrypt(key, ciphertext):
  cipher = XOR.new(key)
  return cipher.decrypt(base64.b64decode(ciphertext))

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp',methods=['POST','GET'])
def signUp():
	try:
		_first_name = request.form['input_first_Name']
		_last_name = request.form['input_last_Name']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']
		#_concent = request.form['concent']
		print request.form, '.......'
		# validate the received values
		if _first_name and _last_name and _email and _password:
			successful = verify_gmail_login(_email, _password)
			if successful:
				# All Good, let's call MySQL
				conn = mysql.connect()
				cursor = conn.cursor()

				encrypted_password = encrypt(secret, _password)
				cursor.callproc('sp_createUser',(_first_name,_last_name,_email,encrypted_password))
				# cursor.callproc('sp_createUser',(_first_name,_last_name,_email,_password))
				data = cursor.fetchall()

				if len(data) is 0:
				    conn.commit()
				    return render_template('finalpage.html')
				    # return json.dumps({'message':'User created successfully !'})
				else:
				    return json.dumps({'error':str(data[0])})
		else:
			return json.dumps({'html':'<span>Enter the required fields</span>'})

	except Exception as e:
	    return json.dumps({'error':str(e)})
	finally:
	    cursor.close() 
	    conn.close()

if __name__ == "__main__":
    app.debug = True
    app.run(port=5002)
