from database import init_mongodb, get_users_collection

if not init_mongodb():
    print("Failed to connect to MongoDB")
    exit(1)

coll = get_users_collection()
print("Indexes on users collection:")
for idx in coll.list_indexes():
    name = idx.get('name')
    key = dict(idx.get('key', {}))
    partial = idx.get('partialFilterExpression')
    sparse = idx.get('sparse', False)
    print(f"- name: {name}")
    print(f"  key: {key}")
    print(f"  partialFilterExpression: {partial}")
    print(f"  sparse: {sparse}\n")

# Helpful check for problematic email index
email_idx = None
for idx in coll.list_indexes():
    key = dict(idx.get('key', {}))
    if 'email' in key:
        email_idx = idx
        break

if email_idx:
    print("Found email index:")
    print(email_idx)
    if not email_idx.get('partialFilterExpression') and not email_idx.get('sparse'):
        print("\n⚠️ The email index is NOT partial/sparse and may cause DuplicateKeyError for missing emails. Consider restarting app to recreate index or dropping the index and creating a partial index:
\n  db.users.dropIndex('<index_name>')
  db.users.createIndex({email: 1}, {unique: true, partialFilterExpression: {email: {$exists: true, $type: 'string'}}})")
else:
    print("Email index looks okay (partial/sparse)")
else:
    print("No email index found")
