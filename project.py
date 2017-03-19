from flask import Flask, render_template, url_for, request, redirect, jsonify, flash
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item


app = Flask(__name__)


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


@app.route('/')
@app.route('/catalog')
def showCategories():
	categories = db_session.query(Category).all()
	latest_items = db_session.query(Item).order_by(desc(Item.c_date)).limit(10).all()
	return render_template('categories.html', categories=categories, items=latest_items)


@app.route('/catalog/<string:category_name>/items')
def showItems(category_name):
	category = db_session.query(Category).filter_by(name=category_name).one()
	items = db_session.query(Item).filter_by(category_id=category.id).all()
	itemsCount = len(items)
	return render_template('items.html', category=category, items=items, count=itemsCount)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
	category = db_session.query(Category).filter_by(name=category_name).one()
	item = db_session.query(Item).filter_by(name=item_name,category_id=category.id).one()
	return render_template('item.html', item=item)


@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItem():
	if request.method == 'POST':
		category = db_session.query(Category).get(request.form['category'])
		newItem = Item(
			name=request.form['name'],
			description=request.form['description'],
			category_id=category.id)
		db_session.add(newItem)
		db_session.commit()
		flash('Item Created')
		return redirect(url_for('showItems', category_name=category.name))
	else:
		categories = db_session.query(Category).all()
		return render_template('newitem.html', categories=categories)

@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
	editedItem = db_session.query(Item).filter_by(name=item_name).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['description']:
			editedItem.description = request.form['description']
		editedItem.category_id = request.form['category']
		db_session.add(editedItem)
		db_session.commit()
		flash('Item Successfully Edited')
		return redirect(url_for('showItem', category_name=editedItem.category.name, item_name=editedItem.name))
	else:
		categories = db_session.query(Category).all()
		return render_template('edititem.html', categories=categories, item=editedItem)

@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
	itemToDelete = db_session.query(Item).filter_by(name=item_name).one()
	if request.method == 'POST':
		db_session.delete(itemToDelete)
		db_session.commit()
		flash('Item Successfully Deleted')
		return redirect(url_for('showItems', category_name=itemToDelete.category.name))
	else:
		return render_template(
			'deleteitem.html',
			item=itemToDelete)


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)