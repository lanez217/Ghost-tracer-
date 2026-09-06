from flask import Flask, jsonify, render_template
import requests, os, hashlib, socket, datetime

app = Flask(__name__)
SITES = {"Instagram":"https://www.instagram.com/{}","TikTok":"https://www.tiktok.com/@{}","X":"https://twitter.com/{}","GitHub":"https://github.com/{}","YouTube":"https://www.youtube.com/@{}","Reddit":"https://www.reddit.com/user/{}/","Telegram":"https://t.me/{}","Pinterest":"https://www.pinterest.com/{}/"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/username/<u>')
def check_user(u):
    res=[]
    for p,url in SITES.items():
        link=url.format(u)
        try:
            ok=requests.get(link,headers={"User-Agent":"Mozilla/5.0"},timeout=5).status_code==200
            s="FOUND" if ok else "Not Found"
        except:
            s="Error"
        res.append({"platform":p,"url":link,"status":s})
    found=len([x for x in res if x['status']=="FOUND"])
    return jsonify({"username":u,"total_found":found,"results":res})

@app.route('/api/email/<path:email>')
def check_email(email):
    email=email.strip().lower()
    md5=hashlib.md5(email.encode()).hexdigest()
    # Legal OSINT footprint links
    footprints = [
        {"platform":"Gravatar","url":f"https://www.gravatar.com/{md5}","desc":"Profile photo linked to email"},
        {"platform":"Google Search","url":f"https://www.google.com/search?q=%22{email}%22","desc":"Public pages mentioning email"},
        {"platform":"GitHub Commits","url":f"https://github.com/search?q={email}&type=commits","desc":"Code commits using this email"},
        {"platform":"HaveIBeenPwned Check","url":f"https://haveibeenpwned.com/account/{email}","desc":"Check if email was in public breach"},
        {"platform":"Paste Search","url":f"https://www.google.com/search?q=site:pastebin.com+%22{email}%22","desc":"Public pastes with email"},
    ]
    return jsonify({
        "email":email,
        "gravatar_url":f"https://www.gravatar.com/avatar/{md5}?d=identicon&s=200",
        "footprints": footprints,
        "risk": "HIGH" if len(email)>0 else "LOW"
    })

@app.route('/api/domain/<domain>')
def check_domain(domain):
    try:
        ip=socket.gethostbyname(domain)
        info={"domain":domain,"ip":ip,"host_info":f"https://who.is/whois/{domain}","shodan":f"https://www.shodan.io/search?query={domain}","google_sites":f"https://www.google.com/search?q=site%3A{domain}"}
        return jsonify(info)
    except Exception as e:
        return jsonify({"error":str(e)})

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get("PORT",5000)))
