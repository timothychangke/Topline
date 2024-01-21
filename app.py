
from newsapi import NewsApiClient
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
import sqlite3
import os
import requests
import re
import datetime as dt
from werkzeug.security import check_password_hash, generate_password_hash
from config import IEX_API_TOKEN, NEWS_API_TOKEN
from additional import api_url, dateintify

newsapi = NewsApiClient(api_key=NEWS_API_TOKEN)
app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

temp = sqlite3.connect("data.db", check_same_thread=False)
db = temp.cursor()

if not os.environ.get("API_TOKEN"):
    raise RuntimeError("API_TOKEN not set")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("title")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if name:
            if username:
                db.execute("SELECT username FROM users WHERE username=?", (username,))
                list = db.fetchall()
                if not list:
                    if password:
                        if confirmation == password:
                            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
                            db.execute("INSERT INTO users (name, username, hash) VALUES (?, ?, ?)", (name, username, password_hash))
                            temp.commit()
                            return redirect("login")
                        else:
                            flash("Passwords do not match", "error")
                            return render_template("register.html")
                    else:
                        flash("Password needs to be filled", "error") 
                        return render_template("register.html")
                else:
                    flash("Username already in use", "error")
                    return render_template("register.html")
            else:
                flash("Username needs to be filled", "error")
                return render_template("register.html")
        else:
            flash("Name needs to be filled", "error")
            return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username:
            db.execute("SELECT * FROM users WHERE username=?", (username,))
            username_list = db.fetchone()
            if username_list:
                if password:
                    db.execute("SELECT hash FROM users WHERE username=?", (username,))
                    hash = db.fetchone()
                    if check_password_hash(hash[0], password):
                        db.execute("SELECT id FROM users WHERE username=?", (username,))
                        session["user_id"] = db.fetchone()
                        db.execute("SELECT name FROM users WHERE username=?", (username,))
                        session["name"] = db.fetchone()
                        return redirect("/")
                    else:
                        flash("Incorrect Password", "error")
                        return render_template("login.html")
                else: 
                    flash("Password cannot be left blank", "error")
                    return render_template("login.html")
            else: 
                flash("Incorrect Username", "error")
                return render_template("login.html")
        else:
            flash("Username needs to be filled", "error")
            return render_template("login.html")
 
    
   
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    print(session)
    return redirect("/login")
        

@app.route("/changename", methods=["GET", "POST"])
def changename():
    if session:
        if request.method == "GET":
            return render_template("changename.html")
        else:
            name = request.form.get("new-name")
            old_name = session["name"]
            user_id = session["user_id"][0]
            if name:
                if name.isalpha():
                    if not name == old_name:
                        db.execute("UPDATE users SET name=? WHERE id=?", (name, user_id))
                        temp.commit()
                        session["name"] = (name, )
                        flash("Name Changed!", "success")
                        return redirect("/")
                    else:
                        flash("New Name same as Previous Name", "error")
                        return render_template("changename.html")
                else:
                    flash("Name cannot contain Numeric Characters", "error")
                    return render_template("changename.html")
            else:
                flash("Name cannot be left blank", "error")
                return render_template("changename.html")
    else:
        return redirect("/")
    


@app.route("/changeusername", methods=["GET", "POST"])
def changeusername():
    print(session)
    if session:
        if request.method == "GET":
            return render_template("changeusername.html")
        else: 
            new_username = request.form.get("new-username")
            password = request.form.get("password")
            user_id = session["user_id"][0]
            if new_username:
                db.execute("SELECT username FROM users WHERE id=?", (user_id,))
                old_username = db.fetchone()
                if not new_username == old_username[0]:
                    if password:
                        db.execute("SELECT hash FROM users WHERE id=?", (user_id,))
                        hash = db.fetchone()
                        if check_password_hash(hash[0], password):
                            db.execute("UPDATE users SET username=? WHERE id=?", (new_username, user_id))
                            temp.commit()
                            flash("Username Changed!", "success")
                            return redirect("/")
                        else:
                            flash("Incorrect Password", "error")
                            return render_template("login.html")
                    else: 
                        flash("Password cannot be left blank", "error")
                        return render_template("login.html")
                else:
                    flash("New Username same as Previous Username", "error")
                    return render_template("changeusername.html")
            else:
                flash("Username cannot be left blank")
                return render_template("changeusername.html", "error")
    else:
        return redirect("/login")


@app.route("/changepassword", methods=["GET", "POST"])
def changepassword():
    if session:
        if request.method == "GET":
            return render_template("changepassword.html")
        else:
            old_password = request.form.get("old-password")
            new_password = request.form.get("new-password")
            user_id = session["user_id"][0]
            if old_password:
                if new_password:
                    db.execute("SELECT hash FROM users WHERE id=?", (user_id,))
                    hash = db.fetchone()
                    if check_password_hash(hash[0], old_password):
                        if not old_password == new_password:
                            password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
                            db.execute("UPDATE users SET hash=? WHERE id=?", (password_hash, user_id))
                            temp.commit()
                            flash("Password Changed!")
                            return redirect("/")
                        else:
                            flash("New Password cannot be the same as Old Password", "error")
                            return render_template("changepassword.html") 
                    else:
                        flash("Password Incorrect", "error")
                        return render_template("changepassword.html") 
                else:
                    flash("New Password cannot be left blank", "error")
                    return render_template("changepassword.html") 
            else:
                flash("Previous Password cannot be left blank", "error")
                return render_template("changepassword.html")       
    else: 
        return redirect("/login")
 
 
@app.route("/", methods=["GET", "POST"])
def index():
    if session:
        user_id = session["user_id"][0]
        db.execute("SELECT * FROM portfolio WHERE user_id=?", (user_id, ))
        all = db.fetchall()
        db.execute("SELECT ticker FROM portfolio WHERE user_id=?", (user_id, ))
        ticker_list = db.fetchall()
        pricenow_list = list()
        pnl_list = list()
        delta_days_list = list()
        total_new_list = list()
        portfolio_value = 0
        if ticker_list:
            for key, ticker in enumerate(ticker_list):
                tempurl = api_url(ticker_list[key][0], "quote")
                r = requests.get(tempurl)
                response = r.json()
                pricenow_list.append(str(round(float(response["previousClose"]), 2)))
            for key, li in enumerate(all):
                total_new_list.append(round(float(li[5]) * float(pricenow_list[key]), 2))
            for index, stock in enumerate(all):
                now = dt.datetime.now()
                buy_time = dt.datetime.strptime(stock[6], "%Y-%m-%d %H:%M:%S")
                delta = now - buy_time
                delta_days_list.append(delta.days)
                price_diff = float(pricenow_list[index]) - float(stock[3])
                pnl = round(price_diff/float(stock[3]), 2)
                pnl_list.append(round(pnl*100.00, 2))
            for item in total_new_list:
                portfolio_value += float(item)
        name_list = list()
        total_list = list()
        db.execute("SELECT name, total FROM portfolio WHERE user_id=?", (user_id,))
        data = db.fetchall()
        users_name = session["name"][0]
        for stock in data:
            name_list.append(stock[0])
            total_list.append(stock[1])
        return render_template("homepage.html", portfolio_value=portfolio_value, total_new_list=total_new_list, users_name=users_name, all=all, prices=pricenow_list, days=delta_days_list, pnl=pnl_list, name_list=name_list, total_list=total_list)
    else:
        return redirect("/login")
       
    
@app.route("/search", methods=["POST"])
def search():
    if session:
        stock_ticker = request.form.get("stock-ticker").lower()
        url = api_url(stock_ticker, "quote")
        r = requests.get(url)
        if r:
            response = r.json()
            logo_url = api_url(stock_ticker, "logo")
            lr = requests.get(logo_url)
            logo_response = lr.json()
            des_url = api_url(stock_ticker, "company")
            des = requests.get(des_url)
            des_response = des.json()
            
            industry = des_response["industry"] 
            website = des_response["website"]
            description = des_response["description"]
            ceo = des_response["CEO"]
            address = des_response["address"] + ", " + des_response["state"] + ", " + des_response["city"] + ", " + des_response["country"]
            phone = des_response["phone"]
            employees = des_response["employees"]
            ytd_change = str(response["ytdChange"] * 100) + "%"
            currency = response["currency"]
            image_url = logo_response["url"]
            ticker = str(response["symbol"]).upper()
            name = response["companyName"]
            price = "$" + str(response["previousClose"])
            market_cap = str(format(int(response["marketCap"] / 1000000), ",")) + " M"
            exchange = response["primaryExchange"]
            pe_ratio = response["peRatio"]
            week_high = "$" + str(response["week52High"])
            week_low = "$" + str(response["week52Low"])
            volume = str(format(int(response["avgTotalVolume"]), ","))
            
            return render_template("search.html", ytd_change=ytd_change, currency=currency, employees=employees, phone=phone, industry=industry, website=website, description=description, ceo=ceo, address=address, image_url=image_url, ticker=ticker, name=name, price=price, market_cap=market_cap, exchange=exchange, pe_ratio=pe_ratio, week_high=week_high, week_low=week_low, volume=volume)

        else: 
            flash("Ticker Symbol Invalid", "error")
            return render_template("homepage.html")
    else:
        return redirect("/login")
    
 
@app.route("/addportfolio", methods=["GET", "POST"])  
def addportfolio():
    if session:
        if request.method == "GET":
            return render_template("addportfolio.html")
        else:
            ticker = request.form.get("ticker").upper()
            price = (request.form.get("price"))
            quantity = request.form.get("quantity")
            date = request.form.get("date")
            user_id = int(session["user_id"][0])
            neg_price_regex = "[A-z]*"
            date_day = date[0:2]
            date_month = date[3:5]
            date_year = date[6:]
            if price and not re.match(price, neg_price_regex):
                price = float(price)
                if quantity and quantity.isdigit():
                    if date:
                        if int(date_day) < 32 and int(date_day) > 0: 
                            if int(date_month) < 13 and int(date_month) > 0: 
                                if int(date_year) < 2023 and int(date_year) > 1970: 
                                    db.execute("SELECT * FROM portfolio WHERE user_id=? AND ticker=?", (user_id, ticker))
                                    x = db.fetchall()
                                    if not x:
                                        url = api_url(ticker, "quote")
                                        r = requests.get(url)
                                        if r:
                                            response = r.json()
                                            buy_datetime = (dt.datetime(int(date_year), dateintify(date_month), dateintify(date_day), 0, 0, 0))
                                            total = (float(quantity) * float(price))
                                            name = response["companyName"]
                                            market_cap = str(format(int(response["marketCap"] / 1000000), ",")) + " M"
                                            price = round(price, 2)
                                            total = round(total, 2)
                                            db.execute("INSERT INTO portfolio (user_id, ticker, name, price, market_cap, quantity, date, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (user_id, ticker, name, str(price), market_cap, quantity, buy_datetime, str(total)))
                                            temp.commit()
                                            flash("Portfolio updated!", "success")
                                            return redirect("/")
                                        else:
                                            flash("Invalid Ticker Symbol", "error")
                                            return redirect("/addportfolio")    
                                    else:
                                        flash("Stock already in portfolio", "error")
                                        return redirect("/addportfolio")
                                else:
                                    flash("Invalid date(year)", "error")
                                    return redirect("/addportfolio")
                            else:
                                flash("Invalid date(month)", "error")
                                return redirect("/addportfolio")
                        else:
                            flash("Invalid date(day)", "error")
                            return redirect("/addportfolio")
                    else:
                        flash("Date cannot be left blank", "error")
                        return redirect("/addportfolio")
                else:
                    flash("Invalid Quantity input", "error")
                    return redirect("/addportfolio")
            else:
                flash("Invalid Price input", "error")
                return redirect("/addportfolio")
    else:
        return redirect("/login") 


@app.route("/removeportfolio", methods=["GET", "POST"])
def removeportfolio():
    if session:
        if request.method == "GET":
            return render_template("removeportfolio.html")
        else:
            user_id = session["user_id"][0]
            remove = request.form.get("remove").upper()
            if remove:
                db.execute("SELECT TICKER FROM portfolio WHERE user_id=?",(user_id, ))
                ticker_temp = db.fetchall()
                ticker_list = list()
                for ticker in ticker_temp:
                    ticker_list.append(ticker[0])
                if remove in ticker_list:
                    db.execute("DELETE FROM portfolio WHERE TICKER=? and user_id=?", (remove, user_id))
                    temp.commit()
                    flash("Stock removed", "success")
                    return redirect("/")
                else:
                    flash("Stock not in portfolio", "error")
                    return redirect("/removeportfolio")
            else:
                flash("Stock Input cannot be left blank", "error")
                return redirect("/removeportfolio")
    else:
        return redirect("/")
    
    
@app.route("/changebuyprice", methods=["GET", "POST"])
def changebuyprice():
    if session:
        if request.method == "GET":
            return render_template("changebuyprice.html")
        else:
            new_price = request.form.get("new_price")
            ticker = request.form.get("ticker").upper()
            user_id = session["user_id"][0]
            if ticker:
                db.execute("SELECT TICKER FROM portfolio WHERE user_id=?",(user_id, ))
                ticker_temp = db.fetchall()
                ticker_list = list()
                for tick in ticker_temp:
                    ticker_list.append(tick[0])
                print(ticker_list)
                print(ticker)
                if ticker in ticker_list:
                    if new_price:
                        if round(float(new_price), 2):
                            new_price = str(round(float(new_price), 3))
                            db.execute("UPDATE portfolio SET price=? WHERE user_id=? AND ticker=?",(new_price, user_id, ticker))
                            temp.commit()
                            db.execute("SELECT quantity FROM portfolio WHERE user_id=? AND ticker=?", (user_id, ticker))
                            temp_quan = db.fetchone()
                            quantity = temp_quan[0]
                            new_total = str(float(new_price) * float(quantity))
                            db.execute("UPDATE portfolio SET total=? WHERE user_id=? AND ticker=?", (new_total, user_id, ticker))
                            flash("New quantity updated", "success")
                            return redirect("/")
                        else:
                            flash("Price Input Invalid", "error")
                            return redirect("/changebuyprice")
                    else:
                        flash("Price Input cannot be empty", "error")
                        return redirect("/changebuyprice")
                else:
                    flash("Stock not in portfolio", "error")
                    return redirect("/changebuyprice")
            else:
                flash("Stock Input cannot be left blank", "error")  
                return redirect("/changebuyprice")
    else:
        return redirect("/")


@app.route("/editquantity", methods=["GET", "POST"])
def editquantity():
    if session:
        if request.method == "GET":
            return render_template("editquantity.html")
        else:
            new_quantity = request.form.get("new_quantity")
            ticker = request.form.get("ticker").upper()
            user_id = session["user_id"][0]
            if ticker:
                db.execute("SELECT TICKER FROM portfolio WHERE user_id=?",(user_id, ))
                ticker_temp = db.fetchall()
                ticker_list = list()
                for tick in ticker_temp:
                    ticker_list.append(tick[0])
                print(ticker_list)
                print(ticker[0])
                if ticker[0] in ticker_list:
                    if new_quantity:
                        if new_quantity.isdigit():
                            db.execute("UPDATE portfolio SET quantity=? WHERE user_id=? AND ticker=?",(new_quantity, user_id, ticker[0]))
                            temp.commit()
                            db.execute("SELECT price FROM portfolio WHERE user_id=? AND ticker=?", (user_id, ticker[0]))
                            temp_price = db.fetchone()
                            price = temp_price[0]
                            new_total = str(float(price) * float(new_quantity))
                            db.execute("UPDATE portfolio SET total=? WHERE user_id=? AND ticker=?", (new_total, user_id, ticker[0]))
                            flash("New quantity updated", "success")
                            return redirect("/")
                        else:
                            flash("Quantity Input Invalid", "error")
                            return redirect("editquantity")
                    else:
                        flash("Quantity Input cannot be empty", "error")
                        return redirect("editquantity")
                else:
                    flash("Stock not in portfolio", "error")
                    return redirect("editquantity")
            else:
                flash("Stock Input cannot be left blank", "error")  
                return redirect("editquantity")
    else:
        return redirect("/")
    
     
@app.route("/news", methods=["GET", "POST"])
def news():
    if session:
        user_id = session["user_id"][0]
        db.execute("SELECT name FROM portfolio WHERE user_id=?", (user_id,))
        name_list = db.fetchall()
        if name_list == None:
            name_list = (("apple stock", ), ("facebook stock", ))
        news_list = list()
        for name in name_list:
            news_list.append((newsapi.get_everything(q=name[0], language="en", page_size=4))["articles"])
        return render_template("news.html", stuff=news_list[0])
    else: 
        return redirect("/")
   
if __name__ == "__main__":
    app.run(debug=True)