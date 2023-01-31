import json
import falcon
import mysql.connector

class bankdb:
    con = None
    cur = None

    __json_content = {}

    def __init__(self):
        pass

    def __validate_json(self, req):
        try:
            self.__json_content = json.loads(req.stream.read())
            print("Valid Input JSON")
            return True
        except ValueError as e:
            self.__json_content = {}
            print("Invalid Input JSON")
            return False

    def create_connection(self):
        self.con = mysql.connector.connect(user='username', password='password',
                              host='127.0.0.1'
                             )
        return self.con

    def close_connection(self):
        self.con.close()

    def create_cursor(self):
        self.cur = self.con.cursor()
        self.cur.execute("Use bankDB")
        return self.cur

    def on_post(self, req, resp):
        self.create_connection()
        self.create_cursor()
        resp.status = falcon.HTTP_201
        validated = self.__validate_json(req)
        output = {}
        if validated:
            insert_sql = 'INSERT INTO bank (customer_id,customer_name,deposit,withdrawel,balance) VALUES (%s, %s, %s, %s, %s)' 
            req_params = self.__json_content
            values = (req_params["customer_id"],req_params["customer_name"],req_params["deposit"],req_params["withdrawel"],req_params["balance"])
            self.cur.execute(insert_sql, values)
            self.con.commit()
            print(f"Record Inserted: {values}")
            output = {
                "msg": "Record Inserted {}".format(values)
            }
        else:
            output = {
                "msg": "Invalid Json Input"
            }
        self.close_connection()
        resp.media = output

    def on_put(self, req, resp):
        self.create_connection()
        self.create_cursor()
        resp.status = falcon.HTTP_200
        req_params = json.loads(req.stream.read())
        if req_params['customer_id']:
            self.cur.execute(f'select * from bank where customer_id = {req_params["customer_id"]}')
            records = self.cur.fetchall()
            balance = 0
            if records:
                records=records[0]
                balance = records['balance']
            if balance:
                if req_params['type'] == 'D':
                    req_params["balance"] = int[balance] + int[req_params["deposit"]]
            update_sql = 'UPDATE bank SET  deposit = %s,withdrawel=%s,balance= %s WHERE customer_id = %s'
            values = (req_params["customer_name"], req_params["deposit"], req_params["withdrawel"], req_params["balance"], req_params["customer_id"])
            self.cur.execute(update_sql,values)
            self.con.commit()
            print(f"Record Updated: {values}")
            output = {
                "msg": "Record Updated {}".format(values)
            }
        else:
            self.cur.execute('select * from bank')
        self.close_connection()
        resp.media = output

    def on_delete(self, req, resp):
        self.create_connection()
        self.create_cursor()
        resp.status = falcon.HTTP_200
        req_params = json.loads(req.stream.read());
        delete_sql = "DELETE FROM bank WHERE customer_id = %(a)s"
        self.cur.execute(delete_sql, {"a": req_params["customer_id"]})
        self.con.commit()
        self.close_connection()
        
    def on_get(self, req, resp):
        self.create_connection()
        self.create_cursor()
        resp.status = falcon.HTTP_200
        params = req.params
        if params:
            self.cur.execute("SELECT * FROM bank WHERE CUSTOMER_NAME = %(a)s", {"a": params["customer_name"]})
        else:
            self.cur.execute("SELECT * FROM bank")
        records = self.cur.fetchall()

        customers = []
        for record in records:
            print(record)
            customer = dict()
            customer["customer_id"] = record[0]
            customer["customer_name"] = record[1]
            customer["deposit"] = record[2]
            customer["withdrawel"] = record[3]
            customer["balance"] = record[4]
            customers.append(customer)

        output = {
            "customers": customers
        }
        self.close_connection()
        resp.media = output

if __name__ == "__main__": 
    pass