import cobol
from dataclasses import asdict
from flask import Flask, request, Response, jsonify
import json
from mpmath import mp
import traceback
import socket


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (cobol.UserAccount, cobol.UserAccounts, cobol.AccountTransaction, cobol.AccountTransactions)):
            return asdict(obj)
        return super().default(obj)


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["JSONIFY_MIMETYPE"] = "application/json; charset=utf-8"


@app.route('/')
def index():
    return f'<h2>Web Services Tier: {socket.gethostname()}</h2>'


@app.route('/api/accounts/<int:id>', methods=['POST'])
def create_account(id):
    try:
        if not request.is_json:
            return jsonify({'error': 'Missing JSON body'}), 400

        data = request.json
        if not data or 'balance_total' not in data:
            return jsonify({'error': 'Missing "balance_total" in JSON body'}), 400

        try:
            balance_total_value = mp.mpf(data.get('balance_total'))
            if balance_total_value < 0:
                return jsonify({'error': f'Invalid balance total value.'}), 422
        except (ValueError, TypeError):
            return jsonify({'error': f'Invalid balance total value.'}), 422

        balance_total = data.get('balance_total')
        account, returnCode = cobol.create_account(id, balance_total)

        if returnCode == "01":
            return jsonify({'error': 'The account key is not correct.'}), 422

        if returnCode != "00":
            return jsonify({'error': 'Cannot process the request.', 'Error code': returnCode}), 500

        json_data = json.dumps(account, cls=CustomEncoder)
        response = Response(json_data, status=200,
                            content_type='application/json')
        return response
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


@app.route('/api/accounts/<int:id>', methods=['GET'])
def read_account(id):
    try:
        account, returnCode = cobol.read_account(id)

        if returnCode == "01":
            return jsonify({'error': 'The account key is not correct.'}), 422

        if returnCode == "03":
            return jsonify({'error': 'The record does not exist.'}), 404

        if returnCode != "00":
            return jsonify({'error': 'Cannot process the request.', 'Error code': returnCode}), 500

        json_data = json.dumps(account, cls=CustomEncoder)
        response = Response(json_data, status=200,
                            content_type='application/json')
        return response
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


@app.route('/api/accounts', methods=['GET'])
def read_accounts():
    try:
        accounts, returnCode = cobol.read_accounts()

        if returnCode != "00":
            return jsonify({'error': 'Cannot process the request.', 'Error code': returnCode}), 500

        json_data = json.dumps(accounts, cls=CustomEncoder)
        response = Response(json_data, status=200,
                            content_type='application/json')
        return response
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


@app.route('/api/accounts/<int:id>/transactions', methods=['POST'])
def create_transaction(id):
    try:
        source_id = id
        if not request.is_json:
            return jsonify({'error': 'Missing JSON body'}), 400

        data = request.json
        if not data or 'destination_id' not in data:
            return jsonify({'error': 'Missing "destination_id" in JSON body'}), 400
        if not data or 'amount' not in data:
            return jsonify({'error': 'Missing "amount" in JSON body'}), 400

        destination_id = 0
        try:
            destination_id = int(data.get('destination_id'))
        except (ValueError, TypeError):
            return jsonify({'error': f'Invalid destination_id value.'}), 422

        if source_id == destination_id:
            return jsonify({'error': f'Invalid destination_id value.'}), 422

        try:
            amount_value = mp.mpf(data.get('amount'))
            if amount_value < 0:
                return jsonify({'error': f'Invalid amount value.'}), 422
        except (ValueError, TypeError):
            return jsonify({'error': f'Invalid amount value.'}), 422

        amount = data.get('amount')
        transaction, returnCode = cobol.create_transaction(
            source_id, destination_id, amount)

        if returnCode == "01":
            return jsonify({'error': 'The account keys are not correct.'}), 422

        if returnCode == "03":
            return jsonify({'error': 'The account does not exist.'}), 404

        if returnCode == "50":
            return jsonify({'error': 'The transaction parameters are not correct.'}), 422

        if returnCode != "00":
            return jsonify({'error': 'Cannot process the request.', 'Error code': returnCode}), 500

        json_data = json.dumps(transaction, cls=CustomEncoder)
        response = Response(json_data, status=200,
                            content_type='application/json')
        return response
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


@app.route('/api/accounts/<int:id>/transactions', methods=['GET'])
def read_transactions(id):
    try:
        type = request.args.get('type', None)
        start_transaction_id_value = request.args.get('start', '0')
        if not start_transaction_id_value.isdigit():
            return jsonify({'error': 'The start transaction value is not correct.'}), 422
        start_transaction_id = int(start_transaction_id_value)

        if type == 'credit':
            transactions, returnCode = cobol.read_credit_transactions(
                id, start_transaction_id)
        elif type == 'debit':
            transactions, returnCode = cobol.read_debit_transactions(
                id, start_transaction_id)
        else:
            return jsonify({'error': 'The transaction type is not correct.'}), 422

        if returnCode == "01":
            return jsonify({'error': 'The account key is not correct.'}), 422

        if returnCode != "00" and returnCode != "03":
            return jsonify({'error': 'Cannot process the request.', 'Error code': returnCode}), 500

        json_data = json.dumps(transactions, cls=CustomEncoder)
        response = Response(json_data, status=200,
                            content_type='application/json')
        return response
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


@app.route('/api/accounts/<int:id>/transactions', methods=['PUT'])
def process_transactions(id):
    try:
        returnCode = cobol.process_transactions(id)

        if returnCode == "01":
            return jsonify({'error': 'The account key is not correct.'}), 422

        if returnCode == "03":
            return jsonify({}), 200

        if returnCode != "00":
            return jsonify({'error': 'Cannot process the request.', 'Error code': returnCode}), 500

        return jsonify({}), 200
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
