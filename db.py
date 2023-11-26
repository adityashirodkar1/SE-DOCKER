from pymongo import MongoClient
connection_string = "mongodb+srv://adishiro:gintoki@cluster0.wlmssnp.mongodb.net/SE?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client.get_database("SE")
users = db.get_collection("users")