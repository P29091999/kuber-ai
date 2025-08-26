from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Connect to MongoDB with environment variable
mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://abhiram:ebGBhxU5cVvDHqAo@nodeexpressprojects.diw08.mongodb.net/test?retryWrites=true&w=majority')
db_name = 'kuber'
use_memory_fallback = False
users_collection = None
try:
	client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
	client.server_info()
	db = client[db_name]
	users_collection = db['users']
	print('✅ Connected to MongoDB')
except Exception as e:
	print(f'⚠️ MongoDB unavailable, using in-memory store. Reason: {e}')
	use_memory_fallback = True
	memory_users = {}

# Simulated price per gram of gold
gold_price_per_gram = 5000

@app.route('/api/purchase-gold', methods=['POST'])
def purchase_gold():
	user_id = request.json.get('userId')
	amount = request.json.get('amount')

	if not user_id or not amount or amount <= 0:
		return jsonify({"error": "Invalid user ID or investment amount."}), 400

	grams_purchased = amount / gold_price_per_gram

	if use_memory_fallback:
		user = memory_users.get(user_id)
		if not user:
			user = {
				"userId": user_id,
				"goldBalance": 0.0,
				"investmentHistory": []
			}
			memory_users[user_id] = user
		user['goldBalance'] = user.get('goldBalance', 0.0) + grams_purchased
		user['investmentHistory'].append({"amount": amount, "grams": grams_purchased, "date": datetime.datetime.now().isoformat()})
		updated_balance = user['goldBalance']
	else:
		user = users_collection.find_one({"userId": user_id})
		if not user:
			user = {
				"userId": user_id,
				"goldBalance": grams_purchased,
				"investmentHistory": [{"amount": amount, "grams": grams_purchased, "date": datetime.datetime.now()}]
			}
			users_collection.insert_one(user)
			updated_balance = grams_purchased
		else:
			new_balance = user['goldBalance'] + grams_purchased
			users_collection.update_one(
				{"userId": user_id},
				{"$set": {"goldBalance": new_balance}},
				{"$push": {"investmentHistory": {"amount": amount, "grams": grams_purchased, "date": datetime.datetime.now()}}}
			)
			updated_balance = new_balance

	return jsonify({
		"message": f"You have successfully purchased {grams_purchased:.2f} grams of digital gold!",
		"transactionId": f"TXN{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
		"updatedGoldBalance": round(updated_balance, 6)
	})

if __name__ == "__main__":
	app.run(debug=True, port=3001)
