from flask import Flask, jsonify, render_template
import requests, os, hashlib, socket, urllib.parse

app = Flask(__name__)
SITES = {"Instagram":"https://www.instagram.com/{}","TikTok":"https://www.tiktok.com/@{}","X":"https://twitter.com/{}","GitHub":"https://github.com/{}","YouTube":"https://www.youtube.com/@{}","Reddit":"https://www.reddit.com/user/{}/","Telegram":"https://t.me/{}","Pinterest":"https://www.pinterest.com/{}/"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/username/<u>')
def check_user(u):
    res=[]
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for p,url in SITES.items():
        link=url.format(u)
        try:
            r=requests.get(link,headers=headers,timeout=6,allow_redirects=True)
            # More accurate check
            if r.status_code==200 and "not found" not in r.text.lower() and "sorry" not in r.text.lower()[:500].lower():
                s="FOUND"
            else:
                s="Not Found"
        except:
            s="Error"
        res.append({"platform":p,"url":link,"status":s})
    found=len([x for x in res if x['status']=="FOUND"])
    return jsonify({"username":u,"total_found":found,"results":res})

@app.route('/api/email/<path:email>')
def check_email(email):
    email=email.strip().lower()
    safe_email=urllib.parse.quote(email)
    md5=hashlib.md5(email.encode()).hexdigest()
    footprints = [
        {"platform":"Gravatar","url":f"https://www.gravatar.com/avatar/{md5}","desc":"Profile photo linked to email"},
        {"platform":"Google Search","url":f"https://www.google.com/search?q=%22{safe_email}%22","desc":"Public pages mentioning email"},
        {"platform":"GitHub Commits","url":f"https://github.com/search?q={safe_email}&type=commits","desc":"Code commits using this email"},
        {"platform":"HaveIBeenPwned","url":f"https://haveibeenpwned.com/account/{safe_email}","desc":"Check if email was in breach"},
        {"platform":"Paste Search","url":f"https://www.google.com/search?q=site%3Apastebin.com+%22{safe_email}%22","desc":"Public pastes"},
    ]
    return jsonify({
        "email":email,
        "gravatar_url":f"https://www.gravatar.com/avatar/{md5}?d=identicon&s=200",
        "footprints": footprints,
        "risk":"HIGH"
    })

@app.route('/api/domain/<domain>')
def check_domain(domain):
    try:
        ip=socket.gethostbyname(domain)
        safe=urllib.parse.quote(domain)
        return jsonify({"domain":domain,"ip":ip,"host_info":f"https://who.is/whois/{domain}","shodan":f"https://www.shodan.io/search?query={safe}"})
    except Exception as e:
        return jsonify({"error":str(e)})

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get("PORT",5000)))
