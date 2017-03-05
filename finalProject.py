from flask import Flask, render_template, url_for, request, redirect, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


app = Flask(__name__)


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/restaurants/JSON')
def restaurantsJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants=[r.serialize for r in restaurants])

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).get(restaurant_id)
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
	item = session.query(MenuItem).get(menu_id)
	return jsonify(MenuItem=item.serialize)


@app.route('/')
@app.route('/restaurant')
def showRestaurants():
	restaurants = session.query(Restaurant).all()
	return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
	if request.method == 'POST':
		newRestaurant = Restaurant(name=request.form['name'])
		session.add(newRestaurant)
		session.commit()
		flash('New Restaurant Created')
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('newrestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
	editedRestaurant = session.query(Restaurant).get(restaurant_id)
	if request.method == 'POST':
		if request.form['name']:
			editedRestaurant.name = request.form['name']
		session.add(editedRestaurant)
		session.commit
		flash('Restaurant Successfully Edited')
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('editrestaurant.html', restaurant=editedRestaurant)

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).get(restaurant_id)
	if request.method == 'POST':
		session.delete(restaurant)
		session.commit()
		flash('Restaurant Successfully Deleted')
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('deleterestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
	restaurant = session.query(Restaurant).get(restaurant_id)
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
	items_by_course = {}
	for item in items:
		if item.course in items_by_course:
			items_by_course[item.course].append(item)
		else:
			items_by_course[item.course] = [item]
	return render_template('menu.html', restaurant=restaurant, items=items_by_course)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
		newItem = MenuItem(
			name=request.form['name'],
			description=request.form['description'],
			price=request.form['price'],
			course=request.form['course'],
			restaurant_id=restaurant_id)
		session.add(newItem)
		session.commit()
		flash('Menu Item Created')
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',
	methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	editedItem = session.query(MenuItem).get(menu_id)
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['description']:
			editedItem.description = request.form['description']
		if request.form['price']:
			editedItem.price = request.form['price']
		editedItem.course = request.form['course']
		session.add(editedItem)
		session.commit
		flash('Menu Item Successfully Edited')
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		return render_template(
			'editmenuitem.html',
			restaurant_id=restaurant_id,
			item=editedItem)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete',
	methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	item = session.query(MenuItem).get(menu_id)
	if request.method == 'POST':
		session.delete(item)
		session.commit()
		flash('Menu Item Successfully Deleted')
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		return render_template(
			'deletemenuitem.html',
			restaurant_id=restaurant_id,
			item=item)


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)