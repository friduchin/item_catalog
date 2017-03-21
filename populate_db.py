from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Base, Category, User, Item
 
engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

categories = ['Soccer', 'Basketball', 'Baseball', 'Frisbee', 'Snowboarding', 'Rock Climbing', 'Skating', 'Hockey', 'Surfing']
for c in categories:
  category = Category(name=c)
  session.add(category)
  session.commit()

user = User(
  name='Daria',
  email='example@gmail.com',
  picture='http://idge.staticworld.net/images/reddit.svg')
session.add(user)
session.commit()

items = [
{
  'name': 'Stick',
  'description': ('Sticks are composed of a long, slender shaft and a flat extension at one end called the blade. ' +
    'The curved part where the blade and the shaft meet is called a taper. ' +
    'The blade is the part of the stick used to contact the puck, and is typically 10 to 15 inches long. ' +
    "Stick dimensions can vary widely, as they are usually built to suit a particular player's size."),
  'category': 'Hockey'
},
{
  'name': 'Goggles',
  'description': ('Protect the eyes from glare and from icy particles flying up from the ground. ' +
    'Double lens anti-fog ski goggles were invented and patented by Robert Earl "Bob" Smith.'),
  'category': 'Snowboarding'
},
{
  'name': 'Snowboard',
  'description': ("Usually the width of one's foot longways, with the ability to glide on snow. " +
    'Snowboards are differentiated from monoskis by the stance of the user. ' +
    'In monoskiing, the user stands with feet inline with direction of travel ' +
    '(facing tip of monoski/downhill) (parallel to long axis of board), ' +
    'whereas in snowboarding, users stand with feet transverse (more or less) to the longitude of the board.'),
  'category': 'Snowboarding'
},
{
  'name': 'Shinguards',
  'description': ("A piece of equipment worn on the front of a player's shin to protect them from injury. " +
    'These are commonly used in soccer. This is due to either being required ' +
    'by the rules/laws of the sport or worn voluntarily by the participants for protective measures.'),
  'category': 'Soccer'
},
{
  'name': 'Frisbee',
  'description': ('A disc-shaped gliding toy or sporting item that is generally plastic ' +
    'and roughly 20 to 25 centimetres (8 to 10 in) in diameter with a lip, ' +
    'used recreationally and competitively for throwing and catching, ' +
    'for example, in flying disc games. The shape of the disc, an airfoil in cross-section, ' +
    'allows it to fly by generating lift as it moves through the air while spinning.'),
   'category': 'Frisbee'
},
{
  'name': 'Bat',
  'description': ('A smooth wooden or metal club used in the sport of baseball ' +
    'to hit the ball after it is thrown by the pitcher. ' +
    'By regulation it may be no more than 2.75 inches (70 mm) in diameter ' +
    'at the thickest part and no more than 42 inches (1,100 mm) long. '+
    'Although historically bats approaching 3 pounds (1.4 kg) were swung, ' +
    'today bats of 33 ounces (0.94 kg) are common, topping out at 34 ounces (0.96 kg) to 36 ounces (1.0 kg).'),
  'category': 'Baseball'
},
{
  'name': 'Soccer Cleats',
  'description': ('Cleats or studs are protrusions on the sole of a shoe, or on an external attachment to a shoe, ' +
    'that provide additional traction on a soft or slippery surface. ' +
    'In American English the term cleats is used synecdochically to refer to shoes featuring such protrusions. ' +
    "Similarly, in British English the term 'studs' can be used to refer to 'football boots' or 'rugby boots', " +
    "for instance, in a similar manner to the way 'spikes' is often used to refer to athletics shoes."),
  'category': 'Soccer'
}
]
for i in items:
  category = session.query(Category).filter_by(name=i['category']).one()
  item = Item(
    name=i['name'],
    description=i['description'],
    category_id=category.id,
    user_id=1)
  session.add(item)
  session.commit()

print "populated!"
