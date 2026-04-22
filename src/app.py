from flask import Flask, request 
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import json
from datetime import datetime
import os
import psycopg2
import random 

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL  not set")


app = Flask(__name__)

def get_db():
    return psycopg2.connect(DATABASE_URL)

conn = get_db()
cursor = conn.cursor()

cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart( id SERIAL PRIMARY KEY,
               phone TEXT,
               item TEXT,
               price INTEGER
              )     
            """)

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
                   id SERIAL PRIMARY KEY,
                   phone TEXT,
                   item TEXT,
                   qty INTEGER,
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


   
   # data["items"] = {k.lower(): v for k, v in data["items"].items()    
    
@app.route("/")
def home():
        return "Service is running"

    
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():  
        resp = MessagingResponse()
        sender = request.values.get("From")
        phone = sender.replace("whatsapp:", "")
        
        #today = datetime.now().strftime("%Y-%m-%d")
        msg = request.values.get("Body","").lower()
        #all_items = list(data["items"].keys()) 
        
        if not msg:
            resp.message("send something")
        
        else:
            msg = msg.lower()    
            
            if user_state.get(phone) == "waiting_quantity":
                msg_clean = msg.replace("plates", "").replace("plate","").strip()
              
                if not msg_clean.isdigit():
                    resp.message("Enter number only(1,2,3...)")
                    
                else: 
                    resp.message("Quantity received")  
                    
            else:
                resp.message("bot working")        
                    
        return str(resp)          
                    
        
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
        if msg in data["greetings"]["keywords"]:
            
              # WELCOME TEXT
             welcome = resp.message(
            "Hi, I am *Shaliss Bot*\n\n"
            "Welcome to *Royal Biryani Restaurant*\n\n"
            "Type *menu* to continue."
            )
            
             # LOGO IMAGE (ONLY FIRST TIME)
             welcome.media("https://res.cloudinary.com/dd4bsgg46/image/upload/v1768571938/Untitled_design_2_t1kqlx.png")
             
             return str(resp)
        
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
        elif msg =="2" or  msg == "category": 
        
            text = "*Categories*\n"
            for cat in data["categories"]:
                text += f"-{cat}\n"
            resp.message(text)    
            return str(resp)
        
        elif msg.lower() in data["categories"].keys():
            
            category = data["categories"][msg.lower()]    
            text = f"*{msg.upper()} Menu*\n\n"
            text += category["response"]
             
            resp.message(text)
            return str(resp)
        
        # item add block
        elif msg in [item.lower() for item in all_items]:
            selected_item[phone] = msg.lower()
            user_state[phone] = "waiting_quantiy"
            
            text = f"{msg.title()} selected\n\n"
            
            #addons 
            if msg.lower() in addons:
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
                f"Whatsapp: {c['whatsapp']}\n"
            ) 
             resp.message(text)
             return str(resp)
        
          #show order   
        elif msg in ["7" ,"show order"] :
            user_cart = cart.get(phone, {})

            if not user_cart:
             resp.message("🛒 Your cart is empty\n👉 Type *menu* to start ordering")
             return str(resp)

            text = "🧾 *Your Order Summary*\n\n"
            total = 0

            for i, (item, qty) in enumerate(user_cart.items(), 1):
               price = data["items"].get(item.lower(),{}).get("price",0)
               item_total = price * qty
               total += item_total

               text += f"{i}. 🍽️ {item.title()} x{qty} = ₹{item_total}\n"

               text += f"\n💰 *Total: ₹{total}*"
               text += "\n\n👉 Type *YES* to confirm your order ✅"

               resp.message(text)
               return str(resp)
            
        elif msg.lower() == "yes":

            user_cart = cart.get(phone, {})
            
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
                  
            if not user_cart:
             resp.message("❌ No order found\n👉 Type *menu* to start")
             return str(resp)

            total = 0
            today = datetime.now().strftime("%Y-%m-%d")

            text = "🎉 *Order Confirmed!*\n\n"
            text += "🧾 *Order Details:*\n\n"

            for i, (item, qty)  in enumerate(user_cart.items(), 1):

              price = data["items"].get(item.lower(),{}).get("price",0)
              
              if price == 0:
                  continue
              
              item_total = price * qty
              total += item_total

              text += f"{i}. 🍽️ {item.title()} x{qty} = ₹{item_total}\n"

             # 💾 SAVE TO DATABASE
              cursor.execute(
                """
                INSERT INTO orders (phone, item, qty, price ,date)
               VALUES (%s,%s,%s,%s,%s)
               """, 
               (phone, item, qty, price, today)
             )

            conn.commit()
            cursor.close()
            conn.close()

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
        

      try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 🔹 TOTAL CUSTOMERS
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]

        # 🔹 TOTAL ORDERS (order_id based)
        cursor.execute("SELECT COUNT(DISTINCT order_id) FROM orders")
        total_orders = cursor.fetchone()[0]

        # 🔹 MONTHLY ORDERS
        cursor.execute("""
            SELECT COUNT(DISTINCT order_id) 
            FROM orders 
            WHERE EXTRACT(MONTH FROM date::date) = EXTRACT(MONTH FROM CURRENT_DATE)
        """)
        monthly_orders = cursor.fetchone()[0]

        # 🔹 NEW CUSTOMERS THIS MONTH
        cursor.execute("""
            SELECT COUNT(*) 
            FROM customers 
            WHERE EXTRACT(MONTH FROM first_order_date::date) = EXTRACT(MONTH FROM CURRENT_DATE)
        """)
        monthly_new = cursor.fetchone()[0]

        # 🔹 REPEAT CUSTOMERS
        cursor.execute("""
            SELECT COUNT(*) FROM customers WHERE total_orders > 1
        """)
        repeat_customers = cursor.fetchone()[0]

        # 🔹 MOST POPULAR DISH
        cursor.execute("""
            SELECT item, COUNT(*) as total 
            FROM orders 
            GROUP BY item 
            ORDER BY total DESC 
            LIMIT 1
        """)
        popular = cursor.fetchone()
        popular_item = popular[0] if popular else "No orders yet"

        # 🔹 RECENT ORDERS (with name + order_id)
        cursor.execute("""
            SELECT o.order_id, c.name, o.item, o.qty, o.price, o.date
            FROM orders o
            LEFT JOIN customers c ON o.phone = c.phone
            ORDER BY o.id DESC
            LIMIT 10
        """)
        recent_orders = cursor.fetchall()

        cursor.close()
        conn.close()

        # 🔹 HTML OUTPUT
        html = f"""
        <h2>📊 Owner Dashboard</h2>

        <p><b>Total Customers:</b> {total_customers}</p>
        <p><b>Total Orders:</b> {total_orders}</p>
        <p><b>Monthly Orders:</b> {monthly_orders}</p>
        <p><b>New Customers:</b> {monthly_new}</p>
        <p><b>Repeat Customers:</b> {repeat_customers}</p>
        <p><b>Most Popular Dish:</b> {popular_item}</p>

        <hr>

        <h3>🧾 Recent Orders</h3>
        <table border="1" cellpadding="8">
        <tr>
            <th>Order ID</th>
            <th>Name</th>
            <th>Item</th>
            <th>Qty</th>
            <th>Price</th>
            <th>Date</th>
        </tr>
        """

        for order in recent_orders:
            html += f"""
            <tr>
                <td>{order[0]}</td>
                <td>{order[1] or "N/A"}</td>
                <td>{order[2]}</td>
                <td>{order[3]}</td>
                <td>{order[4]}</td>
                <td>{order[5]}</td>
            </tr>
            """

        html += "</table>"

        return html
      except Exception as e:
        return f"❌ Error: {e}"

                                
if __name__ ==   "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)                  