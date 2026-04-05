from flask import Flask,request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import json
from datetime import datetime
import os
import sqlite3
import random 

order_counter = 1000
cart = {}
selected_item = {}
user_state = {}
addons = {
    "paneer butter masala":[
        "butter roti",
        "mix veg",
        "dal tadka",
        "cold drink"
        
    ],
    
    "veg biryani":[
        "cold drink",
        "mutton curry",
        "chicken curry"
    ],
    
    "coffee":[
        "brownie",
        "ice cream"
    ],
    
    "samosa":[
        "cold drink",
        "tea",
        "coffee"
    ],
     
     "mix veg":[
         "butter roti",
         "dal tadka",
         "fresh lime"
     ]

}
app = Flask(__name__)

conn = sqlite3.connect("database.db",check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
               CREATE TABLE IF NOT EXISTS cart( id INTEGER PRIMARY KEY AUTOINCREMENT,
               phone TEXT,
               item TEXT,
               price INTEGER
              )     
            """ )

cursor.execute("""
               CREATE TABLE IF NOT EXISTS  customers (
                   phone TEXT PRIMARY KEY,
                   name TEXT,
                   first_order_date TEXT,
                   total_orders INTEGER
                 )  
           """ )

cursor.execute("""
               CREATE TABLE IF NOT EXISTS orders (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   phone TEXT,
                   item TEXT,
                   price INTEGER,
                   date TEXT
                 )  
             """ )

conn.commit()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR,"data.json")


with open(data_path, "r" ,
        encoding="utf-8") as f:
    data = json.load(f) 
    
    data["items"] = {k.lower(): v for k, v in data["items"].items()}
    
    
    @app.route("/")
    def home():
        return "Service is running"

    @app.route("/whatsapp", methods=["POST"])
    def whatsapp_bot():  
        msg = request.values.get("Body","").strip().lower()
        resp = MessagingResponse()
        sender = request.values.get("From")
        phone = sender.replace("whatsapp:", "")
        today = datetime.now().strftime("%Y-%m-%d")
        all_items = list(data["items"].keys())
        
        # quantity
        if user_state.get(phone) == "waiting_quantity":
            msg_clean = msg.replace("plates","").replace("plate","").strip()
            
            
            if not msg_clean.isdigit():
                resp.message("Enter number only(1,2,3...)")
                return str(resp)
            
            qty = int(msg_clean)
            item = selected_item.get(phone)
            if not item:
                resp.message("Please select item again")
                return str(resp)
            
            if phone not in cart:
                cart[phone] = {}
                
            if item in cart[phone]:
                cart[phone][item] += qty
            else:
                cart[phone][item] = qty        
                
            selected_item.pop(phone,None)
            user_state.pop(phone,None)
            
            resp.message(f"{item.title()}x{cart[phone][item]}added to cart\nType menu or order")
            return str(resp)
        
        
        #greetings
        if any(word in msg for word in 
        data["greetings"]["keywords"]) and phone not in data["Customers"]:
                
             data["Customers"][phone] = {
            "first_seen": today, "visits" : 1
                
            }
              # WELCOME TEXT
             welcome = resp.message(
            "Hi, I am *Shaliss Bot*\n\n"
            "Welcome to *Royal Biryani Restaurant*\n\n"
            "Type *menu* to continue."
            )
            
             # LOGO IMAGE (ONLY FIRST TIME)
             welcome.media("https://res.cloudinary.com/dd4bsgg46/image/upload/v1768571938/Untitled_design_2_t1kqlx.png")
             
             return str(resp)
        
        else: 
            data["Customers"][phone]["visits"] += 1
        with open( data_path, "w",
                     encoding="utf-8") as f:
               json.dump(data, f , indent=4) 
         
         #Menu
        if msg == "1" or msg == "menu":
            text = ("*Main Menu*\n\n"
                    "1 or menu\n"
                    "2 or category\n"
                    "3 or timing\n"
                    "4 or  location\n"
                    "5 or  offers\n"
                    "6 or contact\n"
                    "7 or show order\n\n"
                    "Type any option to continue."
                    )
            
            resp.message(text)
            return str(resp)
              
            #CATEGORIES
        elif msg.startswith("2") or  msg == "category": 
        
            text = "*Categories*\n"
            for cat in data["categories"]:
                text += f"-{cat}\n"
            resp.message(text)
            return str(resp)  
        
        elif msg.lower() in data["categories"]:    
            
            category = data["categories"][msg.lower()]    
            text = f"*{msg.upper()} Menu*\n\n"
            text += category["response"]
             
            resp.message(text)
            return str(resp)
        
        # item add block
        elif msg in all_items:
            selected_item[phone] = msg
            user_state[phone] = "waiting_quantity"
            
            text = f"{msg.title()} selected\n\n"
            
            #addons 
            if msg in addons:
                text += "You may also like:\n"
                for add in addons[msg]:
                    text += f".{add}\n"
                    
            text += "\nRecommended for 2 people:\n2 plates\n\n"        
            text += "How many plates would you like?\n"
            text += "1 /2 /3 / Custom"
            resp.message(text)
            return str(resp)       
        
            #TIMING
        elif msg == "3" or msg == "timing":
             resp.message(data["timing"]["response"]) 
             return str(resp)
             
             #LOCATION
        elif msg == "4" or msg == "location":
             loc = data["location"] 
             text = (f"{loc['address']}\n{loc['google_map']}")
             resp.message(text)
             return str(resp)  
            
            # OFFERS
        elif msg == "5" or  msg == "offers":
            resp.message(f"*Today`s Offers*\n{data['offers']}")
            return str(resp)
    
            #CONTACT
        elif msg == "6" or msg == "contact":
             c = data["contact"] 
             text = (
                f"*Contact*\n" 
                f"Phone: {c['phone']}\n"  
                f"Whatsapp: {c['whatsapp']}"
            ) 
             resp.message(text)
             return str(resp)
         
        
          #show order   
        elif msg in ["7" ,"show order"] :
            user_cart = cart.get(phone, {})

            if not user_cart:
             resp.message("🛒 Your cart is empty\n👉 Type *menu* to add items")
             return str(resp)

            text = "🧾 *Your Order Summary*\n\n"
            total = 0

            for i, (item, qty) in enumerate(user_cart.items(), 1):
               price = data["items"].get(item.lower(), 0)
               item_total = price * qty
               total += item_total

               text += f"{i}. 🍽️ {item.title()} x{qty} = ₹{item_total}\n"

               text += f"\n💰 *Total: ₹{total}*"
               text += "\n\n👉 Type *YES* to confirm your order ✅"

               resp.message(text)
               return str(resp)
            
        elif msg == "yes":

            user_cart = cart.get(phone, {})

            if not user_cart:
             resp.message("❌ No order found\n👉 Type *menu* to start")
             return str(resp)

            total = 0
            today = datetime.now().strftime("%Y-%m-%d")

            text = "🎉 *Order Confirmed!*\n\n"
            text += "🧾 *Order Details:*\n\n"

            for i, (item, qty) in enumerate(user_cart.items(), 1):

              price = data["items"].get(item.lower(), 0)
              
              if price == 0:
                  continue
              
              item_total = price * qty
              total += item_total

              text += f"{i}. 🍽️ {item.title()} x{qty} = ₹{item_total}\n"

             # 💾 SAVE TO DATABASE
              cursor.execute(
            "INSERT INTO orders (phone, item, qty, price, date) VALUES (?, ?, ?, ?, ?)",
            (phone, item, qty, price, today)
             )

            conn.commit()

            text += f"\n💰 *Total Paid: ₹{total}*"
            text += "\n\n⏳ Your order will be ready in 20-30 mins"
            text += "\n📞 Restaurant will contact you soon"
            text += "\n❤️ Thank you for ordering!"

            resp.message(text)

            # 🧹 clear cart
            cart.pop(phone, None)

            return str(resp)
         
         # ANY ITEM NAME 
        else:  
            confused_words = ["?" , "help", "kya", "kaise","what"]
            
            if any(word in msg for word in confused_words):
              resp.message("Sorry Type *menu* to continue.")
            return str(resp)
            
                
    @app.route("/admin")
    def admin_dashboard():
        
        #TOTAL Customers 
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]
        
        # total Orders 
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        #MONTHLY ORDERS 
        cursor.execute("""
                       SELECT COUNT(*) FROM orders WHERE strftime('%m', date) = strftime('%m','now')
                       """)
        monthly_orders = cursor.fetchone()[0]
        
        # New customers this month 
        cursor.execute("""
                       SELECT COUNT(*) FROM customers WHERE strftime('%m', first_order_date) = strftime('%m','now')
                       """)
        monthly_new = cursor.fetchone()[0]
        
        #Repeat Customers 
        cursor.execute("""
                       SELECT COUNT(*) FROM customers  WHERE total_orders > 1
                       """)   
        repeat_customers = cursor.fetchone()[0]
        
        # Most Popular Dish 
        cursor.execute("""
                       SELECT item, COUNT(*) as total FROM orders GROUP BY item ORDER BY total DESC LIMIT 1
                       """) 
        popular = cursor.fetchone()
        
        popular_item = popular[0] if popular else "NO orders yet"
        
        
        return f"""
         <h2>Owner Dashboard</h2>
         <p>Total Customers: {total_customers} </p>
         <p>Total Orders: {total_orders}</p>
         <p>Monthly Orders: {monthly_orders}</p>
         <p>New Customers This Month:
         {monthly_new}</p>
         <p>Repeat Customers:
         {repeat_customers}</p>
          <p>Most Popular Dish: {popular_item}</p>
          
          """ 
                           
if __name__ ==   "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)                  