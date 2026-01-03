from database import init_mongodb, get_users_collection
init_mongodb()
users = list(get_users_collection().find({}, {'_id':0,'username':1,'email':1,'user_id':1,'created_at':1}).sort('created_at', -1).limit(50))
print('Recent users (most recent first):')
for u in users:
    print(u)
