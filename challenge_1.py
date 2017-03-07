import MySQLdb
from flask import Flask, request
import json

#DB details of MySQL database
HOSTIP = "192.168.43.48"
USERNAME = "root"
PASSWORD = "*****"
DBNAME = "sqdb"

app = Flask(__name__, static_url_path='')


@app.route('/user/create', methods=['POST'])
def create_user():
    """
    Method used to create a new user using the data passed
    in the body of POST request.
    """
    data = request.data
    dataDict = json.loads(data)
    username = dataDict['username']
    first_name = dataDict['fname']
    last_name = dataDict['lname']
    address = dataDict['address']
    try:
        #check if username already exists
        db = MySQLdb.connect(host=HOSTIP, user=USERNAME, passwd=PASSWORD, db=DBNAME)
        c = db.cursor(MySQLdb.cursors.DictCursor)
        query = 'SELECT * FROM User where username = "' + username + '"'
        c.execute(query)
        user_details = c.fetchone()
        if user_details:
            return "Username already exists"

        #get the last userid used
        last_usrid_query = 'SELECT userid FROM User ORDER BY userid DESC LIMIT 1'
        c.execute(last_usrid_query)
        last_userid = c.fetchone()
        if last_userid:
            id = int(last_userid['userid'][3:])
            userid = "usr" + str(id+1)
        else:
            userid = "usr1"

        #Add into User Table
        ins_user_query = 'INSERT INTO User VALUES ("%s","%s","%s","%s")' %(userid, username, first_name, last_name)
        c.execute(ins_user_query)

        #get the last addrid used
        last_addrid_query = 'SELECT add_id FROM Address ORDER BY add_id DESC LIMIT 1'
        c.execute(last_addrid_query)
        last_addrid = c.fetchone()
        if last_addrid:
            id = int(last_addrid['add_id'][3:])
            addid = "add" + str(id + 1)
        else:
            addid = "add1"

        #Add into Address table
        ins_addr_query = 'INSERT INTO Address VALUES ("%s","%s","%s")' %(addid, userid, address)
        c.execute(ins_addr_query)
        db.commit()
        return "Successfully added new user"

    except Exception:
        return "Failed to add new user"


@app.route('/userlist')
def get_user_list():
    """
    Method to return the user list
    """
    users_dict = {"users":[]}
    try:
        db = MySQLdb.connect(host=HOSTIP, user=USERNAME, passwd=PASSWORD, db=DBNAME)
        c = db.cursor(MySQLdb.cursors.DictCursor)
        query = 'SELECT * FROM User'
        c.execute(query)
        user_list = c.fetchall()

        for user in user_list:
            new_dict = {}
            new_dict['fname'] = user['fname']
            new_dict['lname'] = user['lname']
            userid = user['userid']
            addr_query = 'SELECT * FROM Address where user_id = "' + userid + '"'
            c.execute(addr_query)
            addr_details = c.fetchone()
            if addr_details:
                new_dict['address'] = addr_details['address']
            else:
                new_dict['address'] = '[]'
            users_dict['users'].append(new_dict)

        return json.dumps(users_dict)

    except Exception:
        return "Failed to fetch user list"

@app.route('/user')
def get_user_details():
    """
    Method to fetch the user details based on the userid passed as query string
    e.g. GET operation on /user?userid=usr1 will return the details of the user
    with the userid 'usr1'
    """
    userid = request.args.get('userid')
    out_dict = {"user":{}}
    try:
        db = MySQLdb.connect(host=HOSTIP, user=USERNAME, passwd=PASSWORD, db=DBNAME)
        c = db.cursor(MySQLdb.cursors.DictCursor)
        query = 'SELECT * FROM User where userid = "' + userid + '"'
        c.execute(query)
        user_details = c.fetchone()
        addr_query = 'SELECT * FROM Address where user_id = "' + userid + '"'
        c.execute(addr_query)
        addr_details = c.fetchone()

        if user_details:
            new_dict = {}
            new_dict['fname'] = user_details['fname']
            new_dict['lname'] = user_details['lname']
            new_dict['address'] = addr_details['address']
            out_dict['user'] = new_dict
        return json.dumps(out_dict)

    except Exception:
        return "Failed to fetch user details"


@app.route('/')
def default_handler():
    return "Hello There"


if __name__ == '__main__':
    app.run(debug=True)
