from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
api = Api(app, title='Your API', version='1.0', description='Your API description')

# Namespace for items
ns = api.namespace('items', description='Operations related to items')

NAV_API_URL = "http://ABM-NAV2017.abmgroup.co.ke:7048/DynamicsNAV100/ODataV4/Company('Chloride%20Exide%20Kenya%20Ltd')/ProductsAPI"
NAV_USERNAME = "mzito"
NAV_PASSWORD = "Abmgrp@2019"

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
        return None


# Function to retrieve a single item by item number
def get_item_by_number(item_number):
    query_url = f"{NAV_API_URL}?$filter=No. eq '{item_number}'"
    response = requests.get(query_url, auth=HTTPBasicAuth(NAV_USERNAME, NAV_PASSWORD))
    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        return None


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


if __name__ == '__main__':
    app.run(debug=True)