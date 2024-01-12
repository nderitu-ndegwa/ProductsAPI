from flask import Flask
from flask_restx import Api, Resource
import requests

app = Flask(__name__)
api = Api(app)

NAV_API_ENDPOINT = "http://ABM-NAV2017.abmgroup.co.ke:7047/DynamicsNAV100/WS/Chloride%20Exide%20Kenya%20Ltd/Page/ProductsAPI"


@api.route('/get_all_products')
class AllProducts(Resource):
    def get(self):
        try:
            response = requests.get(NAV_API_ENDPOINT)
            data = response.json()
            products = [{"No.": item['No.'], "Description": item['Description']} for item in data['value']]
            return products
        except Exception as e:
            return {"error": str(e)}


@api.route('/get_product_details/<string:item_no>')
class ProductDetails(Resource):
    def get(self, item_no):
        try:
            response = requests.get(f"{NAV_API_ENDPOINT}?$filter=No. eq '{item_no}'")
            data = response.json()
            if data['value']:
                item = data['value'][0]
                details = {
                    "No.": item['No.'],
                    "Description": item['Description'],
                    "Inventory": item['Inventory'],
                    "Unit Price": item['UnitPrice'],
                    "Capacity Rating": item['CapacityRating'],
                    "Voltage": item['Voltage']
                }
                return details
            else:
                return {"error": f"Item with No. {item_no} not found."}
        except Exception as e:
            return {"error": str(e)}


if __name__ == '__main__':
    app.run(debug=True)