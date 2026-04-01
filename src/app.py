from flask import Flask,request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import json
from datetime import datetime
import os
import sqlite3
import random 

order_counter = 1000
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
                    "7 or order\n\n"
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
        
          #item add block
          
        elif any(item in msg.lower() for item in data["items"]):
            
            for item in data["items"]:
                if item in msg.lower():
                    selected_item[phone] = item
                    user_state[phone] = "waiting_quantity"
                    break

            text = f"{item.title()} selected 🍽️\n\n"
            if item in addons:
                text += "\n\nYou may also like:\n"
                for add in addons[item]:
                    text += f"- {add}\n"
            
            text += "\nRecommended for 2 people:\n"
            text += "2 plates\n\n"
            text += "How many plates would you like?\n\n"
            text += " 1️⃣ 1 plate\n"
            text += " 2️⃣ 2 plates\n"
            text += " 3️⃣ 3 plates\n"
            text += " 4️⃣ Custom"

            resp.message(text)
            return str(resp)  
          
        elif msg.isdigit() and user_state.get(phone) == "waiting_quantity":

            qty = int(msg)
            item = selected_item.get(phone)

            price = data["items"][item]

            for i in range(qty):
               cursor.execute(
            "INSERT INTO cart (phone , item, price) VALUES (?, ?, ?)",
            (phone, item, price)
             )
            conn.commit()

            selected_item.pop(phone, None)
            user_state.pop(phone, None)
            
            text = f"{item.title()} x{qty} added to cart\n\n"
            text += "You can order more items\n"
            text += "Type *menu* to continue ordering\n"
            text += "Type *order OR 7* to checkout"

            resp.message(text)
            return str(resp)
            
         # show order
        elif msg.lower() in ["show order" , "cart"]:
            
            cursor.execute(
                "SELECT item, price FROM cart WHERE phone = ?",
                (phone,)
            )
            items = cursor.fetchall()
            
            if not items:
                resp.message("Your cart is empty.")
                return str(resp)
            
            text = " *Your Current Order*\n\n"
            total = 0
            
            for i, row in enumerate(items, 1):
                item_name = row[0]
                price = row[1]
                
                text += f"{i}. {item_name.title()} - $ {price}\n"
                total += price
                
            text += f"\n Total: ${total}"
                
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
             
             
        #ORDER
        elif msg == "7" or msg == "order":
            
            cursor.execute(
                "SELECT item, price FROM cart WHERE phone = ?",
                (phone,)
            )
            items = cursor.fetchall()
            
            if not items:
                resp.message("Your cart is empty.")
                return str(resp)
            
            # build confirmation message ==
            total = 0
            
            global order_counter
            order_counter += 1
            order_id = order_counter
            
            cart_summary = {}

            for item_name, price in items:
                if item_name in cart_summary:
                   cart_summary[item_name]["qty"] += 1
                   cart_summary[item_name]["total"] += price
            else:
                cart_summary[item_name] = {"qty": 1, "total": price}

            text = f"*Order Confirmed*\n\nOrder ID: {order_id}\n\n"

            for i, (item, details) in enumerate(cart_summary.items(), 1):
             text += f"{i}. {item.title()} x{details['qty']} - Rs.{details['total']}\n"

            total = sum(d["total"] for d in cart_summary.values())
            text += f"\nTotal: Rs.{total}"
            text += "\n\nRestaurant will contact you soon."
    
            # tracking start here ====
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone ,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                               UPDATE customers
                               SET total_orders = total_orders + 1
                               WHERE phone = ? 
                               """ , (phone,)) 
                
                conn.commit()   
                
            else:
                cursor.execute("""
                               INSERT INTO customers (phone,
                               name, first_order_date, total_orders) 
                               VALUES (?, ?, ? , 1)
                               """, (phone, "Guest", today)) 
                
            for row in items:
                cursor.execute("""
                               INSERT INTO orders (phone, item, price, date) 
                               VALUES (?,?,?,?)
                               """, (phone, row[0], row[1], today)) 
            
            conn.commit()
            
                 # tracking end here=====    
          
                # Clear cart after order 
            cursor.execute("DELETE FROM cart WHERE phone = ?", (phone,))
            conn.commit()
            
            resp.message(text)    
            return str(resp)
         
        #bye 
        elif msg in data["bye"]["keywords"]:
            resp.message(data["bye"]["response"])
            return str(resp)  
            
        
         # ANY ITEM NAME 
        else:  
            confused_words = ["?" , "help", "kya", "kaise"]
            
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