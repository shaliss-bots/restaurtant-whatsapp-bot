from flask import Flask,request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import json
from datetime import datetime
import os
app = Flask(__name__)

with open("src/data.json", "r" ,
        encoding="utf-8") as f:
    data = json.load(f)
    
    
    @app.route("/")
    def home():
        return "Service is running"

    @app.route("/whatsapp", methods=["POST"])
    def whatsapp_bot():
        msg = request.form.get("Body").strip().lower()
        resp = MessagingResponse()
        sender = request.form.get("From")
        phone = sender.replace("whatsapp:", "")
        today = datetime.now().strftime("%Y-%m-%d")
        
        if phone not in data["Customers"]:
            data["Customers"][phone] ={
                "first_seen": today, "visits" : 1
                
            }
            
             # WELCOME TEXT
            msg = resp.message(
            "Hi, I am *Shaliss Bot*\n\n"
            "Welcome to *Royal Biryani Restaurant*\n\n"
            "Type *menu* to continue."
            )
             # LOGO IMAGE (ONLY FIRST TIME)
            msg.media("https://res.cloudinary.com/dd4bsgg46/image/upload/v1768571938/Untitled_design_2_t1kqlx.png")
        else: 
            data["Customers"][phone]["visits"] += 1
        
    
            
            
     #POPULAR DISH TRACK
        popular = data["stats"]["Popular_dishes"]
        if msg in popular:
            popular[msg] += 1
        else:
            popular[msg] = 1
            
        data["stats"]["Popular_dishes"] = popular
        
         #MONTHLY STATS
        month = datetime.now().strftime("%Y-%m") 
        monthly= data["stats"]["Monthly"]   
        if month in monthly:
         monthly[month] += 1
        else:
         monthly[month] = 1
         data["stats"]["Monthly"] = monthly      
                
    
         
         #Menu
        if msg == "1" or msg == "menu":
            text = "*Full Menu*\n\n"
            text += data["veg_menu"]["response"] + "\n\n"
            text += data["non_veg_menu"]["response"] + "\n\n"
            text += data["snacks"]["response"] +  "\n\n"
            text += data["drinks"]["response"] + "\n\n"
            text += data["desserts"]["response"] 
            
            resp.message(text)
                
              #CATEGORIES
        elif msg == "2" or msg == "categories":
        
            text = "*Categories*\n"
            for cat in data["categories"]:
                text += f"-{cat}\n"
            resp.message(text)
             
            #TIMING
        elif msg == "3" or msg == "timing":
             t = data["timings"] 
             text =(
                f"*Timings*\n{t['days']}\n{t['open']}- {t['close']}"
            ) 
             resp.message(text) 
             
             #LOCATION
        elif msg == "4" or msg == "location":
             loc = data["location"] 
             text = (f"{loc['address']}\n{loc['google_map']}")
             resp.message(text)
             
            
            # OFFERS
        elif msg == "5" or  msg == "offers":
            text = "*Today's Offers*\n"
            for offer in data["offers"]:
                text += f"- {offer}\n"
            resp.message(text)
    
            #CONTACT
        elif msg == "6" or msg == "contact":
             c = data["contact"] 
             text = (
                f"*Contact*\n" 
                f"Phone: {c['phone']}\n"  
                f"Whatsapp: {c['whatsapp']}"
            ) 
             resp.message(text)
             #ORDER
        elif msg == "7" or msg == "order":
             resp.message(data["order_note"])
                 
                  # ANY ITEM NAME 
        else:
             resp.message(data["bye"]["response"])  
             
         

        return str(resp)
    
if __name__ ==   "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)                    