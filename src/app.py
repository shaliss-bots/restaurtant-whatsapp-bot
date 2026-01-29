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
            
         # LOGO IMAGE (ONLY FIRST TIME)
            img = resp.message()
            image_msg.media("https://res.cloudinary.com/dd4bsgg46/image/upload/v1768571938/Untitled_design_2_t1kqlx.png")
            text_msg = resp.message()
        
         # WELCOME TEXT
            resp.message(
            "Hi, I am *Shaliss Bot*\n\n"
            "Welcome to *Royal Biryani Restaurant*\n\n"
            "Type *menu* to continue."
            )
            return str(resp)
    
        else: 
            data["Customers"][phone][visits] += 1 
    
            
            
     #POPULAR DISH TRACK
        popular = data["stats"]["Popular_dishes"]
        if msg in popular:
            popular[msg] += 1
        else:
            popular[msg] = 1
            
        data["stats"]["Popular_dishes"] = popular
        
         #MONTHLY STATS
        month = datatime.now().strftime("%Y-%m") 
        monthly= data["stats"]["Monthly"]   
        if month in monthly:
         monthly[month] += 1
        else:
         monthly[month] = 1
         data["stats"]["Monthly"] = monthly      
                
    
         
         #Menu
        if msg == "1" or msg == "menu":
            text = "*Full Menu*\n\n"
            
            for category, items in data ["menu"].items():
                text += f"*{category.upper()}*\n"
                
            for item in items:
                text += f"-{item['name']} : ${item['price']}\n"    
                text += "\n"
                
                reply.body(text)
                
        #CATEGORIES
            if msg == "2" or msg == "categories":
        
             text = "*Categories*\n"
            for cat in data["categories"]:
                text += f"-{cat}\n"
                reply.body(text)
            #TIMING
            if msg == "3" or msg == "timing":
             t = data["timings"] 
            reply.body(
                f"*Timings*\n{t['days']}\n{t['open']}- {t['close']}"
            )  
             #LOCATION
            if msg == "4" or msg == "location":
             loc = data["location"] 
            reply.body(f"{loc['address']}\n{loc['google_map']}")
            
            # OFFERS
            if msg == "5" or  msg == "offers":
             text = "*Today's Offers*\n"
            for offer in data["offers"]:
                text += f"- {offer}\n"
                reply.body(text)
    
            #CONTACT
            if msg == "6" or msg == "contact":
             c = data["contact"] 
            reply.body(
                f"Phone: {c['phone']}\n  Whatsapp: {c['whatsapp']}"
            ) 
            
             #ORDER
            if msg == "7" or msg == "order":
             reply.body(data["order_note"])
                 
            # ANY ITEM NAME 
            else:
             reply.body(data["thank_you"])  
            reply.body(text)
         
            with open("src/data.json","w",encoding="utf-8") as f:
             json.dump(data,f,indent=2)
        
             return str(resp)
    
if __name__ ==   "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)                    