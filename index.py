from flask import Flask, render_template , request , redirect, url_for , session, make_response, jsonify
from flask_bcrypt import Bcrypt
import requests
import random
import pandas as pd
from flask_pymongo import PyMongo


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_pyfile('config.py')

# Initialize PyMongo with the Flask app
mongo = PyMongo(app)


@app.route('/', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username' : request.form['username']})

        if login_user:
            if bcrypt.check_password_hash(login_user['password'], request.form['password']):
                session['username'] = request.form['username']
                return render_template('index.html')

        return render_template("login.html")
    
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username' : request.form['username']})
        if existing_user is None:
            hashpass = bcrypt.generate_password_hash(request.form['password'], 10)
            #hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect('/index')
        
        return 'Username already exists!'

    return render_template('register.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/customers', methods = ['POST', 'GET'])
def customers():
    if request.method == 'POST':
        name = request.form['name']
        customers = mongo.db.users.find({'username': name})
        return render_template('customer.html', customers = customers)

    customers = mongo.db.users.find()
    return render_template('customer.html', customers = customers)


@app.route('/vehicle')
def vehicle():
    access_key = "pmu5mu8GBt3Ehl4B65zfS_9FWFeyBuq6PqV9IMiqZlY"
    count = 50
    base_url = 'https://api.unsplash.com'
    endpoint = '/search/photos'
    image_urls = []
    
    # Parameters for the Unsplash API request
    params = {
        'query': 'car',
        'per_page': count,
        'client_id': access_key,
    }
    
    # Make the API request
    response = requests.get(f"{base_url}{endpoint}", params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Extract image URLs from the response
        results = response.json()['results']
        image_urls = [result['urls']['regular'] for result in results]
        # return image_urls
    
    df = pd.read_csv('./static/Car details v3.csv')

    cars = []
    for i in range(50):
        obj = df.iloc[i]
        obj['naav'] = df.iloc[i]['name']
        obj['link'] = image_urls[random.randint(0, len(image_urls) - 1)]
        cars.append(obj)


    return render_template('vehicle.html', cars = cars)


@app.route('/book/<index>')
def book(index):
    i = int(index)
    df = pd.read_csv('./static/Car details v3.csv')
    pend_car = df.iloc[i]
    pend_car = df.iloc[i]
    pend_car['naav'] = df.iloc[i]['name']
    pend_car['rent'] = pend_car['seats'] * 100
    return render_template('book.html', car = pend_car, ind = i)


@app.route('/bill/<rent>', methods = ['POST'])
def bill(rent):
    if request.method == 'POST':
        bill = request.form
        user = mongo.db.users.find_one({'name': session['username']})
        arr = rent.split("-")
        df = pd.read_csv('./static/Car details v3.csv')
        column_value = df.loc[int(arr[1]), "name"]
        
        user_query = {'username': session['username']}
        user_update = {'$set': {'vehicle': column_value, 'hours': bill['hours']}}
        result = mongo.db.users.update_one(user_query, user_update)
    
        amt = float(arr[0])*int(bill['hours'])
        temp = amt
        if bill['driver'] == 'y':
            amt += 2000
        return render_template('bill.html', bill = bill, amt = amt, rent = rent, temp = temp)


@app.route('/addVehicle', methods = ['POST', 'GET'])
def addVehicle():
    if request.method == 'POST':
        car = request.form
        seller_type = 'Individual'
        year = 2023
        new_row_data = [car['name'], int(year), int(car['price']), int(car['km']), car['fuel'], 'Individual', 'Auto', car['owner'], car['mileage'] + 'kmpl', car['engine'], '90 bhp', '109Nm@ 4500rpm', int(car['seats'])]
        df = pd.read_csv('./static/Car details v3.csv')
    
        new_row = pd.DataFrame([new_row_data], columns=df.columns)
        df = pd.concat([new_row, df], ignore_index=True)
        df.to_csv('./static/Car details v3.csv', index=False)

        return redirect('/vehicle')

    return render_template('add.html') 

@app.route('/removeVehicle/<i>', methods = ['GET'])
def removeVehicle(i):
    index = int(i)
    df = pd.read_csv('./static/Car details v3.csv')
    df = df.drop(index)
    df.to_csv('./static/Car details v3.csv', index=False)
    return  redirect('/vehicle')

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect('/')

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)