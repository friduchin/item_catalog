from flask import Flask
from flask import render_template, url_for, request, redirect, make_response
from flask import flash, jsonify
from flask import session as login_session
from functools import wraps

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import random
import string
import httplib2
import json
import requests


app = Flask(__name__)

# Get client id fo Google auth
CLIENT_ID = json.loads(
    open('g_client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('g_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid
    access_token = credentials.access_token
    url = (('https://www.googleapis.com/oauth2/v1/tokeninfo' +
            '?access_token=%s') % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was error in the accesstoken info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID does not match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for latter use
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check if user already exists in the DB and store it if it does not
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px; border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150 px;'
    flash('You are now logged in as %s' % login_session['username'])
    return output


def gdisconnect():
    # Only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user is not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Send message that the user is diconnected
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason the token was invalid.
        response = make_response(
                json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print 'path: %s' % request.path
    print 'method: %s' % request.method
    print 'token: %s' % access_token

    # Exchange client token for long-lived server-side token
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = (('https://graph.facebook.com/oauth/access_token' +
            '?grant_type=fb_exchange_token&client_id=%s&client_secret=%s' +
            '&fb_exchange_token=%s') % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    # Strip expire tag from access token
    token = result.split('&')[0]
    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # The token must be stored in the login_session in order to properly logout
    # Let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = (('https://graph.facebook.com/v2.8/me/picture' +
            '?%s&redirect=0&height=200&width=200') % token)
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']

    # Check if user already exists in the DB and store it if it does not
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px; border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150 px;'
    flash('You are now logged in as %s' % login_session['username'])
    return output


def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = (('https://graph.facebook.com/%s/permissions' +
            '?access_token=%s') % (facebook_id, access_token))
    h = httplib2.Http()
    h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash('You have successfully been logged out')
        return redirect(url_for('showCategories'))
    else:
        flash('You were not logged in to begin with')
        return redirect(url_for('showCategories'))


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


def getUserId(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def loginRequired(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash('You are not allowed to access there. Please log in first.')
            return redirect(url_for('showLogin'))
    return decoratedFunction


@app.route('/')
@app.route('/catalog')
def showCategories():
    categories = db_session.query(Category).all()
    latest_items = db_session.query(Item).order_by(
        desc(Item.c_date)).limit(10).all()
    return render_template(
        'categories.html', categories=categories, items=latest_items)


@app.route('/catalog/<string:category_name>/items')
def showItems(category_name):
    category = db_session.query(Category).filter_by(name=category_name).one()
    items = db_session.query(Item).filter_by(category_id=category.id).all()
    itemsCount = len(items)
    return render_template(
        'items.html', category=category, items=items, count=itemsCount)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    category = db_session.query(Category).filter_by(name=category_name).one()
    item = db_session.query(Item).filter_by(
        name=item_name, category_id=category.id).one()
    return render_template('item.html', item=item, creator=item.user)


@app.route('/catalog/item/new', methods=['GET', 'POST'])
@loginRequired
def newItem():
    if request.method == 'POST':
        category = db_session.query(Category).get(request.form['category'])
        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=category.id,
            user_id=login_session['user_id'])
        db_session.add(newItem)
        db_session.commit()
        flash('Item Created')
        return redirect(url_for('showItems', category_name=category.name))
    else:
        categories = db_session.query(Category).all()
        return render_template('newitem.html', categories=categories)


@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
@loginRequired
def editItem(item_name):
    editedItem = db_session.query(Item).filter_by(name=item_name).one()
    if editedItem.user_id != login_session['user_id']:
        flash('Items May Be Edited Only By Its Creator')
        return redirect(url_for(
            'showItem',
            category_name=editedItem.category.name,
            item_name=editedItem.name))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        editedItem.category_id = request.form['category']
        db_session.add(editedItem)
        db_session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for(
            'showItem',
            category_name=editedItem.category.name,
            item_name=editedItem.name))
    else:
        categories = db_session.query(Category).all()
        return render_template(
            'edititem.html', categories=categories, item=editedItem)


@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
@loginRequired
def deleteItem(item_name):
    itemToDelete = db_session.query(Item).filter_by(name=item_name).one()
    category = itemToDelete.category
    if itemToDelete.user_id != login_session['user_id']:
        flash('Items May Be Deleted Only By Its Creator')
        return redirect(url_for(
            'showItem',
            category_name=category.name,
            item_name=itemToDelete.name))
    if request.method == 'POST':
        db_session.delete(itemToDelete)
        db_session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showItems', category_name=category.name))
    else:
        return render_template('deleteitem.html', item=itemToDelete)


# JSON APIs to view Catalog Information
@app.route('/catalog/JSON')
def catalogJSON():
    categories = db_session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/catalog/category/<int:category_id>/JSON')
def categoryJSON(category_id):
    category = db_session.query(Category).get(category_id)
    items = db_session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/item/<int:item_id>/JSON')
def itemJSON(item_id):
    item = db_session.query(Item).get(item_id)
    return jsonify(Item=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
