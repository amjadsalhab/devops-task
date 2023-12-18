from flask import Flask, request
import requests
from flask_sqlalchemy import SQLAlchemy
import boto3
import os

def create_app(test_config=None):
    app = Flask(__name__)
    
    if test_config is None:
        # Load the configuration from the SSM Parameter Store as in your main.py
        app.config['SQLALCHEMY_DATABASE_URI'] = db_connection_string
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 20}
    else:
        # Load the test configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
        app.config['TESTING'] = True
    app.app_context().push()
    db = SQLAlchemy(app)
    #db.create_all()
    return app, db

environment=os.getenv('ENVIRONMENT')
service_name=os.getenv('SERVICE_NAME')



# Create a boto3 client for SSM
ssm_client = boto3.client('ssm', region_name='us-east-1')

# Retrieve the database connection string from SSM Parameter Store
db_connection_string = ssm_client.get_parameter(
    Name=f"/{environment}/{service_name}/db_connection_string",  # replace with the name of your parameter
    WithDecryption=True  # if the parameter value is encrypted
)['Parameter']['Value']

user_service_base_url = ssm_client.get_parameter(
    Name=f"/{environment}/{service_name}/user_service_base_url",  # replace with the name of your parameter
    WithDecryption=True  # if the parameter value is encrypted
)['Parameter']['Value']


app,db=create_app()

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product = db.Column(db.String(50), nullable=False)
##db.create_all()
@app.route('/health', methods=['GET'])
def health():
    
    return {'status': "healthy"}, 200

@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    new_order = Order(user_id=data['user_id'], product=data['product'])
    db.session.add(new_order)
    db.session.commit()
    return {'id': new_order.id}, 201

@app.route('/order/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    order = Order.query.get_or_404(order_id)
    
    return {'product': order.product, 'user': order.user_id}, 200

@app.route('/orders/all', methods=['GET'])
def get_all_orders():
    endpoint=f"{user_service_base_url}/users"
    print(f"getting all users from {endpoint}")
    users = requests.get(endpoint).json()['users']
    all_orders = []
    for user in users:
        user_orders = Order.query.filter_by(user_id=user['id']).all()
        orders_data = [{'id': order.id, 'product': order.product, 'user_id': order.user_id} for order in user_orders]
        all_orders.extend(orders_data)
    return {'orders': all_orders}, 200