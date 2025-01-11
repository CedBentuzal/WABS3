from dbs_connect import connect_to_db

async def create_account(first_name, last_name, email, user_name, cellphone_number, password_hash):
    conn = await connect_to_db()
    if conn is None:
        return {'status': 'Failed', 'message': 'Database connection failed.'}

    try:
        async with conn.transaction():  
           
            client_query = """
            INSERT INTO Client (first_name, last_name, email)
            VALUES ($1, $2, $3) RETURNING client_id;
            """
            client_id = await conn.fetchval(client_query, first_name, last_name, email)

            
            account_query = """
            INSERT INTO Account (client_id, user_name, cellphone_number, password_hash)
            VALUES ($1, $2, $3, $4);
            """
            await conn.execute(account_query, client_id, user_name, cellphone_number, password_hash)

        
            balance_query = """
            INSERT INTO Balance (client_id, amount)
            VALUES ($1, 0);
            """
            await conn.execute(balance_query, client_id)

        return {'status': 'Success', 'message': 'Account created successfully.'}

    except Exception as e:
        
        return {'status': 'Failed', 'message': f'An error occurred: {e}'}

    finally:
        await conn.close()


async def log_in(cellphone_number, password):
      conn = await connect_to_db()
      if conn is None:
            return {'status': 'Failed', 'message': 'Database connection failed.'}
      
      try:
          import hashlib
          password_hash = hashlib.sha256(password.encode()).hexdigest() 

          query = """
          SELECT client_id, user_name
          FROM Account
          WHERE cellphone_number = $1 AND password_hash = $2 
          """
          result = await conn.fetchrow(query, cellphone_number, password_hash)

          if result:
                return{
                      'status':'success', 'message': 'log in success',
                      'user': {
                            'client_id':result['client_id'],
                            'user_name':result['user_name']
                            
                      }
                }
          else:
                  return {'status': 'failed', 'message': 'Invalid credentials.'}
      except Exception as e:
        return {'status': 'failed', 'message': f'An error occurred: {e}'}
      finally:
         await conn.close()

async def dash_board(client_id):
    conn = await connect_to_db()
    if conn is None:
        return {'status': 'Failed', 'message': 'Database connection failed.'}

    try:
        query = """
        SELECT A.user_name, B.amount
        FROM Account A
        LEFT JOIN Balance B ON A.client_id = B.client_id
        WHERE A.client_id = $1
        """
        result = await conn.fetchrow(query, client_id)


        if result:
            return {
                'status': 'success',
                'user': {
                    'user_name': result['user_name'],
                    'balance': result['amount']
                }
            }
        else:
            return {'status': 'failed', 'message': 'User not found.'}
    except Exception as e:
        return {'status': 'failed', 'message': f'An error occurred: {e}'}
    finally:
        await conn.close()

async def delete_account(client_id):
    conn = await connect_to_db()
    if conn is None:
        return {'status': 'Failed', 'message': 'Database connection failed.'}

    try:
        delete_query = """
        DELETE FROM Client 
        WHERE client_id = $1
        """
        result = await conn.execute(delete_query, client_id)

        if result == 'DELETE 1':  
            return {'status': 'success', 'message': 'Account successfully deleted.'}
        else:
            return {'status': 'failed', 'message': 'Account not found or already deleted.'}
    except Exception as e:
        return {'status': 'failed', 'message': f'An error occurred: {e}'}
    finally:
        await conn.close()

async def send_amount(sender_client_id, recipient_cellphone, amount):
    conn = await connect_to_db()
    if conn is None:
        return {'status': 'Failed', 'message': 'Database connection failed.'}

    try:
        
        async with conn.transaction():
            
            sender_balance_query = """
            SELECT amount FROM Balance WHERE client_id = $1
            """
            sender_balance = await conn.fetchval(sender_balance_query, sender_client_id)

            if sender_balance is None:
                return {'status': 'failed', 'message': 'Sender not found.'}
            
            if sender_balance < amount:
                return {'status': 'failed', 'message': 'Insufficient balance.'}

           
            recipient_client_id_query = """
            SELECT client_id FROM Account WHERE cellphone_number = $1
            """
            recipient_client_id = await conn.fetchval(recipient_client_id_query, recipient_cellphone)

            if not recipient_client_id:
                return {'status': 'failed', 'message': 'Recipient not found.'}

            
            update_sender_balance_query = """
            UPDATE Balance SET amount = amount - $1 WHERE client_id = $2
            """
            await conn.execute(update_sender_balance_query, amount, sender_client_id)

           
            update_recipient_balance_query = """
            UPDATE Balance SET amount = amount + $1 WHERE client_id = $2
            """
            await conn.execute(update_recipient_balance_query, amount, recipient_client_id)

        return {'status': 'success', 'message': 'Amount sent successfully.'}

    except Exception as e:
        return {'status': 'failed', 'message': f'An error occurred: {e}'}

    finally:
        await conn.close()