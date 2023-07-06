from flask import Flask, render_template, request, url_for
import sqlite3 as sql
import datetime

app = Flask(__name__)

@app.route('/home')
def home():
   return render_template('sales.html')

@app.route('/enternew')
def new():
   return render_template('student.html')

@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            nm = request.form['nm']
            quant = request.form['quantity']
            
            with sql.connect("Sales.db") as con:
                cur = con.cursor()
                
                cur.execute("SELECT price FROM menu WHERE name=?", (nm,))
                price = cur.fetchone()[0]
                price = int(price)

                cur.execute("SELECT raw FROM menu WHERE name=?", (nm,))
                rawp = cur.fetchone()[0]
                rawp = int(rawp) * int(quant)
                
                # Calculate the cost as quantity * price
                tcost = int(quant) * int(price)
                tprofit = tcost - rawp
                current_date = datetime.date.today().strftime("%Y-%m-%d")
                cur.execute("SELECT COUNT(*) FROM stocks WHERE odate = ?", (current_date,))
                count = cur.fetchone()[0]

                # If the date exists, update the stock quantity
                if count > 0:
                    if nm == 'coffee':
                        update_query = "UPDATE stocks SET coffee_stock = coffee_stock - ? WHERE odate = ?"
                    elif nm == 'cake':
                        update_query = "UPDATE stocks SET cake_stock = cake_stock - ? WHERE odate = ?"
                    elif nm == 'samosa':
                        update_query = "UPDATE stocks SET samosa_stock = samosa_stock - ? WHERE odate = ?"

                    cur.execute(update_query, (quant, current_date,))
                    con.commit()
                else:
                    # If the date does not exist, insert a new row with default values
                    insert_query = "INSERT INTO stocks (odate, cake_stock, coffee_stock, samosa_stock) VALUES (?, 100, 100, 100)"
                    cur.execute(insert_query, (current_date,))
                    con.commit()

                    if nm == 'coffee':
                        update_query = "UPDATE stocks SET coffee_stock = coffee_stock - ? WHERE odate = ?"
                    elif nm == 'cake':
                        update_query = "UPDATE stocks SET cake_stock = cake_stock - ? WHERE odate = ?"
                    elif nm == 'samosa':
                        update_query = "UPDATE stocks SET samosa_stock = samosa_stock - ? WHERE odate = ?"

                    cur.execute(update_query, (quant, current_date,))
                    con.commit()

                cur.execute("INSERT INTO orders (name, quantity, cost, odate, profit) VALUES (?, ?, ?, ?, ?)",
                            (nm, quant, tcost, current_date, tprofit))
                con.commit()

                cur.execute("UPDATE menu SET stock = stock - ? WHERE name = ?", (quant, nm))
                con.commit()
                msg = "Record successfully added"

        except Exception as e:
            con.rollback()
            msg = "Error in insert operation: " + str(e)

        finally:
            con.close()
            return render_template("result1.html", msg=msg)



@app.route('/list')
def list():
   con = sql.connect("sales.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from menu")
   
   rows = cur.fetchall(); 
   return render_template("list.html",rows = rows)
   

@app.route('/')
def analytics():
    con = sql.connect("Sales.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    cur.execute("SELECT coffee_stock FROM stocks")
    trem1 = cur.fetchone()[0]
    cur.execute("SELECT cake_stock FROM stocks")
    trem2 = cur.fetchone()[0]
    cur.execute("SELECT samosa_stock FROM stocks")
    trem3 = cur.fetchone()[0]

    trem =trem1+trem2+trem3
    tsold = int(((300 - trem)/300)*100)
    trem = 100 - tsold

    cur.execute("Select oid,name,quantity,cost,odate from orders")
    rows = cur.fetchall()

    current_date = datetime.date.today().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(quantity) FROM orders WHERE odate=?",(current_date,))
    torders = cur.fetchone()[0]

    # Calculate total income for today
    
    cur.execute("SELECT SUM(cost) FROM orders WHERE odate=?", (current_date,))
    tincome = cur.fetchone()[0]
    print(tincome)

    # Calculate total profit for today

    cur.execute("SELECT SUM(profit) FROM orders WHERE odate=?", (current_date,))
    tprof = cur.fetchone()[0]
    

    cur.execute("SELECT cake_stock FROM stocks WHERE odate=?", (current_date,))
    cakec   = cur.fetchone()[0]
    cakerem = 100- cakec

    cur.execute("SELECT coffee_stock FROM stocks WHERE odate=?", (current_date,))
    coffeec = cur.fetchone()[0]
    coffeerem = 100 - coffeec

    cur.execute("SELECT samosa_stock FROM stocks WHERE odate=?", (current_date,))
    samosac = cur.fetchone()[0]
    samosarem = 100-samosac

    

    return render_template("sales.html", total_orders=torders, total_income=tincome, total_profit=tprof, rows=rows, trem=trem, tsold=tsold, total_cake=cakec, total_coffee=coffeec, total_samosa=samosac,cake_rem=cakerem,coffee_rem=coffeerem,samosa_rem=samosarem,currdate=current_date)
    # return render_template("sales.html")

if __name__ == '__main__':
   app.run(debug = True)