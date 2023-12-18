from flask import Flask, request
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
ssm_client = boto3.client('ssm' , region_name='us-east-1')

# Retrieve the database connection string from SSM Parameter Store
db_connection_string = ssm_client.get_parameter(
    Name=f"/{environment}/{service_name}/db_connection_string",  # replace with the name of your parameter
    WithDecryption=True  # if the parameter value is encrypted
)['Parameter']['Value']

app,db=create_app()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

@app.route('/health', methods=['GET'])
def health():
    return {'status': "healthy"}, 200
    
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(name=data['name'])
    db.session.add(new_user)
    db.session.commit()
    return {'id': new_user.id}, 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_data = [{'id': user.id, 'name': user.name} for user in users]
    return {'users': users_data}, 200
    
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return {'name': user.name}, 200