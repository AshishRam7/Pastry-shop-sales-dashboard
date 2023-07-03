from flask import Flask, render_template, request, url_for
import sqlite3 as sql
import datetime

app = Flask(__name__)

@app.route('/home')
def home():
   return render_template('sales.html')

@app.route('/enternew')
def new_student():
   return render_template('student.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            nm = request.form['nm']
            quant = request.form['quantity']
            # cost = request.form['city']
            # pin = request.form['pin']
            
            with sql.connect("Sales.db") as con:
                cur = con.cursor()
                cur.execute("SELECT price FROM menu WHERE name=?", (nm,))
                price = cur.fetchone()[0]
                price = int(price)

                cur.execute("SELECT raw FROM menu WHERE name=?", (nm,))
                rawp = cur.fetchone()[0]
                rawp = int(rawp) * int(quant)
                print(price)
                print(rawp)
                print(quant)
                # Calculate the cost as quantity * price
                tcost = int(quant) * int(price)
                print(tcost)
                tprofit = tcost - rawp
                current_date = datetime.date.today().strftime("%Y-%m-%d")
                cur.execute("INSERT INTO orders(name,quantity,cost,odate,profit)VALUES(?,?,?,?,?)",(nm,quant,tcost,'2023-06-28',tprofit))
                
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"
        
        finally:
            return render_template("result1.html",msg = msg)
            con.close()

@app.route('/list')
def list():
   con = sql.connect("sales.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from task")
   
   rows = cur.fetchall(); 
   return render_template("list.html",rows = rows)

@app.route('/')
def analytics():
    con = sql.connect("Sales.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    cur.execute("SELECT SUM(stock) FROM menu")
    trem = cur.fetchone()[0]
    tsold = int(((300 - trem)/300)*100)
    trem = 100 - tsold

    cur.execute("Select oid,name,quantity,cost from orders")
    rows = cur.fetchall()

    cur.execute("SELECT COUNT(quantity) FROM orders")
    torders = cur.fetchone()[0]

    # Calculate total income for today
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    cur.execute("SELECT SUM(cost) FROM orders WHERE odate=?", ('2023-06-28',))
    tincome = cur.fetchone()[0]
    print(tincome)

    # Calculate total profit for today

    cur.execute("SELECT SUM(profit) FROM orders WHERE odate=?", ('2023-06-28',))
    tprof = cur.fetchone()[0]

    return render_template("sales.html", total_orders=torders, total_income=tincome, total_profit=tprof, rows=rows, trem=trem, tsold=tsold)
    # return render_template("sales.html")

if __name__ == '__main__':
   app.run(debug = True)