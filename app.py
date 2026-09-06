from flask import Flask, jsonify, render_template, request
import requests, os, hashlib, socket

app = Flask(__name__)

SITES = {
    "Instagram": "https://www.instagram.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "X": "https://twitter.com/{}",
    "GitHub": "https://github.com/{}",
    "YouTube": "https://www.youtube.com/@{}",
    "Reddit": "https://www.reddit.com/user/{}/",
    "Telegram": "https://t.me/{}",
    "Pinterest": "https://www.pinterest.com/{}/",
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/username/<username>')
def check_user(username):
    results=[]
    for plat,url in SITES.items():
        link=url.format(username)
        try:
            r=requests.get(link,headers={"User-Agent":"Mozilla/5.0"},timeout=5)
            status="FOUND" if r.status_code==200 else "Not Found"
        except:
            status="Error"
        results.append({"platform":plat,"url":link,"status":status})
    found=len([x for x in results if x['status']=="FOUND"])
    return jsonify({"username":username,"total_found":found,"results":results})

@app.route('/api/email/<path:email>')
def check_email(email):
    h=hashlib.md5(email.lower().encode()).hexdigest()
    return jsonify({"email":email,"gravatar_url":f"https://www.gravatar.com/avatar/{h}?d=identicon","google_link":f"https://www.google.com/search?q=%22{email}%22"})

@app.route('/api/domain/<domain>')
def check_domain(domain):
    try:
        ip=socket.gethostbyname(domain)
        return jsonify({"domain":domain,"ip":ip})
    except Exception as e:
        return jsonify({"error":str(e)})

if __name__=='__main__':
    port=int(os.environ.get("PORT",5000))
    app.run(host='0.0.0.0',port=port)