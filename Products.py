from flask import Flask, render_template, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from requests.auth import HTTPBasicAuth as RequestsHTTPBasicAuth
import requests
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
api = Api(app, title='Products API', version='1.0', description='API to fetch item nav items')

auth = HTTPBasicAuth()

# Namespace for items
ns = api.namespace('items', description='Operations related to items')

NAV_API_URL = "http://ABM-NAV2017.abmgroup.co.ke:7048/DynamicsNAV100/ODataV4/Company('Chloride%20Exide%20Kenya%20Ltd')/ProductsAPI"
NAV_USERNAME = "Mzito"  
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
@auth.login_required
def get_all_items():
    response = requests.get(NAV_API_URL, auth=RequestsHTTPBasicAuth(NAV_USERNAME, NAV_PASSWORD))
    if response.status_code == 200:
        return response.json().get('value', [])
    elif response.status_code == 401:
        raise requests.exceptions.RequestException(f"Authentication failed. Please check your credentials.")
    else:
        raise requests.exceptions.RequestException(f"Error in request: {response.status_code} - {response.text}")

# Function to retrieve a single item by item number
@auth.login_required
def get_item_by_number(item_number):
    query_url = f"{NAV_API_URL}?$filter=No. eq '{item_number}'"
    response = requests.get(query_url, auth=RequestsHTTPBasicAuth(NAV_USERNAME, NAV_PASSWORD))
    if response.status_code == 200:
        return response.json().get('value', [])
    elif response.status_code == 401:
        raise requests.exceptions.RequestException(f"Authentication failed. Please check your credentials.")
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
    return render_template('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Item API Interaction</title>
            <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
        </head>
        <body>

        <h1>Item API Interaction</h1>

        <label for="itemNumber">Enter Item Number:</label>
        <input type="text" id="itemNumber" placeholder="Item Number">
        <button onclick="getAllItems()">Get All Items</button>
        <button onclick="getSingleItem()">Get Single Item</button>

        <div id="result"></div>

        <script>
            function getAllItems() {
                $.get("/items/all", function(data) {
                    displayResult(data);
                });
            }

            function getSingleItem() {
                var itemNumber = $("#itemNumber").val();
                $.get("/items/" + itemNumber, function(data) {
                    displayResult(data);
                });
            }

            function displayResult(data) {
                var resultDiv = $("#result");
                resultDiv.empty();

                if (Array.isArray(data) && data.length > 0) {
                    for (var i = 0; i < data.length; i++) {
                        resultDiv.append("<p>" + JSON.stringify(data[i]) + "</p>");
                    }
                } else {
                    resultDiv.text("No data found.");
                }
            }
        </script>

        </body>
        </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
