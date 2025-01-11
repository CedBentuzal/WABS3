from flask import Flask, redirect, render_template, request, jsonify, url_for
from dbs import create_account as db_create_account, log_in, dash_board, delete_account, send_amount
import hashlib

app = Flask(__name__, template_folder="templates")

@app.route('/', methods=['GET', 'POST'])
async def log_in_view():
    if request.method == 'GET':
        return render_template('index.html')
    
    if request.method == 'POST':
        cellphone_number = request.form.get('cellphone_number')
        password = request.form.get('password')

        result = await log_in(cellphone_number, password)

        if result['status'] == 'success':
            client_id = result['user']['client_id']
            return redirect(f'/dash_board/{client_id}')
        else:
            return jsonify({'error': result['message']})

@app.route('/logout')
def logout_view():
    return redirect('/')

@app.route('/dash_board/<int:client_id>', methods=['GET', 'POST'])
async def dash_board_view(client_id):
    result = await dash_board(client_id)
    
    if result['status'] == 'success':
        user_data = result['user']
        user_data['client_id'] = client_id  
        return render_template('dash_board.html', user=user_data)
    else:
        return jsonify({"error": result.get("message", "Unknown error occurred.")})

@app.route('/delete_account/<int:client_id>', methods=['POST'])
async def delete_account_view(client_id):
    result = await delete_account(client_id)
    if result['status'] == 'success':
        return redirect('/')
    else:
        return render_template('dash_board.html', user={'client_id': client_id, 'message': result['message']})

@app.route('/send_amount/<int:client_id>', methods=['POST'])
async def send_amount_view(client_id):
    recipient_cellphone = request.form.get('recipient_cellphone')
    amount = request.form.get('amount')

    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'status': 'failed', 'message': 'Amount must be greater than zero.'})
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'Invalid amount.'})

    result = await send_amount(client_id, recipient_cellphone, amount)

    if result['status'] == 'success':
        return redirect(f'/dash_board/{client_id}')
    else:
        return jsonify({'status': 'failed', 'message': result['message']})

@app.route('/create_account', methods=['GET', 'POST'])
async def create_account_view():
    if request.method == 'GET':
        return render_template('create_account.html')
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        user_name = request.form.get('user_name')
        cellphone_number = request.form.get('cellphone_number')
        password = request.form.get('password')

        if not cellphone_number.isdigit() or len(cellphone_number) != 10:
            return render_template("create_account.html", error="Invalid cellphone number.")

        if not password or len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long."})
     
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        result = await db_create_account(first_name, last_name, email, user_name, cellphone_number, password_hash)

        if not isinstance(result, dict) or 'status' not in result:
            return jsonify({"error": "Unexpected error occurred while creating account."})

        if result["status"] == "success":
            return jsonify({"message": "Account successfully created."})
        else:
            return jsonify({"error": result.get("message", "Unknown error occurred.")})

if __name__ == '__main__':
    app.run(debug=True)


