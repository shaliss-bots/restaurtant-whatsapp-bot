from flask import Flask,request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import json
from datetime import datetime
import os
app = Flask(__name__)
order_list = []

with open("src/data.json", "r" ,
        encoding="utf-8") as f:
    data = json.load(f)
    
    
    @app.route("/")
    def home():
        return "Service is running"

    @app.route("/whatsapp", methods=["POST"])
    def whatsapp_bot():
        global order_list
        msg = request.form.get("Body").strip().lower()
        resp = MessagingResponse()
        sender = request.form.get("From")
        phone = sender.replace("whatsapp:", "")
        today = datetime.now().strftime("%Y-%m-%d")
        
        if phone not in data["Customers"]:
            data["Customers"][phone] ={
                "first_seen": today, "visits" : 1
                
            }
            with open("src/data.json", "w",
                      encoding="utf-8") as f:
                json.dump(data, f , indent=4)
            
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

         
         #Menu
        if msg == "1" or msg == "menu":
            text = ("*Menu Categories*\n\n"
                    ". veg\n"
                    ". Non-veg\n"
                    ". Snacks\n"
                    ". Drinks\n"
                    ". Desserts\n\n"
                    "Type category name to view items"
                    )
            
            resp.message(text)
            return str(resp)
                
              #CATEGORIES
        elif msg == "2" or msg == "categories":
        
            text = "*Categories*\n"
            for cat in data["categories"]:
                text += f"-{cat}\n"
            resp.message(text)
            return str(resp) 
        
        
         # ITEM CHECK 
     
            for cat_name, cat_data in data["categories"].items():
                
                    for item in cat_data["Items"]:
                       if item.lower() in msg :
                        order_list.append(item)
                        resp.message(f"{item} added\nType 7 to view order")
                        return str(resp)
                    
                    
        
        elif msg in data["categories"]:
            category = data["categories"][msg]
            
            text = f"*{msg.upper()} Menu*\n\n"
            text += category["response"]
             
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
            resp.message(f"*Today`s Offers*\n{data ['offers']}")
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
            
            if len(order_list)  == 0:
             resp.message("your cart empty")
             return str(resp)
         
            text = "*Your Order*\n\n"
            
            for i in order_list:
                text += f" - {i}\n"
                
            text += "\nType YES to confirm"
            
            resp.message(text)
            return str(resp)
        
        #confirm
        elif msg == "yes":
            if len(order_list) == 0:
                resp.message("No order")
                return str(resp)
            
            resp.message("0rder Confirmed\nThank you")
            order_list.clear()
            return str(resp)   
        
        
        #bye 
        elif msg in data["bye"]["keywords"]:
            resp.message(data["bye"]["response"])  
            
        
         # ANY ITEM NAME 
        else:  
            resp.message(
                "Sorry, I didn't understand.Type menu.MYY LIFE\n"
                 "1 or menu\n"
                 "2 or categories\n"
                 "3 or timing\n"
                 "4 or location\n"
                 "5 or offers\n"
                 "6 or contact\n"
                 "7  or order"
                 
                 
             )
            return str(resp)
    
if __name__ ==   "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)                  