from flask import Flask, render_template, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

load_dotenv()  

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
api = Api(app, title='Products API', version='1.0', description='API to fetch item nav items')

# Namespace for items
ns = api.namespace('items', description='Operations related to items')

# Update the OData URL
NAV_API_URL = "http://ABM-NAV2017.abmgroup.co.ke:7048/DynamicsNAV100/OData/Company('Chloride%20Exide%20Kenya%20Ltd')/ProductsAPI"

# Use your environment variables for NAV credentials
NAV_USERNAME = os.getenv("NAV_USERNAME", "")
NAV_PASSWORD = os.getenv("NAV_PASSWORD", "")

# Model for item
item_model = api.model('Item', {
    'No.': fields.String(required=True, description='Item Number'),
    'Description': fields.String(required=True, description='Item Description'),
    'Inventory': fields.Integer(required=True, description='Inventory'),
    'Unit Price': fields.Float(required=True, description='Unit Price'),
    'Inventory Posting Group': fields.String(required=True, description='Inventory Posting Group'),
    'Item Disc. Group': fields.String(required=True, description='Item Discount Group'),
})

# Function to retrieve all items
def get_all_items():
    response = requests.get(NAV_API_URL, auth=HTTPBasicAuth(NAV_USERNAME, NAV_PASSWORD))
    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        raise requests.exceptions.RequestException(f"Error in request: {response.status_code} - {response.text}")

# Function to retrieve a single item by item number
def get_item_by_number(item_number):
    query_url = f"{NAV_API_URL}?$filter=No. eq '{item_number}'"
    response = requests.get(query_url, auth=HTTPBasicAuth(NAV_USERNAME, NAV_PASSWORD))
    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        raise requests.exceptions.RequestException(f"Error in request: {response.status_code} - {response.text}")

# Resource for getting all items
@ns.route('/all')
class AllItemsResource(Resource):
    def get(self):
        items = get_all_items()
        return items

# Resource for getting a single item by item number
@ns.route('/<string:item_number>')
class SingleItemResource(Resource):
    def get(self, item_number):
        item = get_item_by_number(item_number)
        return item

# Route to serve the integrated HTML page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
