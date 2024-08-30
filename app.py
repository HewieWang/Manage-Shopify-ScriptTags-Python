from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'your_generated_secret_key'

api_key = "6666"
api_secret = "6666"
redirect_uri = "https://5ff1022c.r15.cpolar.top/auth/callback"
scopes = "write_script_tags,read_script_tags"
access_token = None
shop = "harvey-teststore.myshopify.com"

def get_existing_script_tags():
    url = f"https://{shop}/admin/api/2024-07/script_tags.json"
    headers = {"X-Shopify-Access-Token": access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    script_tags = response.json().get("script_tags", [])
    return script_tags

@app.route('/')
def index():
    if access_token:
        script_tags = get_existing_script_tags()
        return render_template('index.html', script_tags=script_tags)
    else:
        return redirect(url_for('auth'))

@app.route('/auth')
def auth():
    install_url = f"https://{shop}/admin/oauth/authorize?client_id={api_key}&scope={scopes}&redirect_uri={redirect_uri}"
    return redirect(install_url)

@app.route('/auth/callback')
def auth_callback():
    global access_token
    code = request.args.get('code')
    if not code:
        flash('Authorization failed.')
        return redirect(url_for('index'))
    
    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": api_key,
        "client_secret": api_secret,
        "code": code
    }
    response = requests.post(token_url, json=payload)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        flash('Authorization successful.')
        return redirect(url_for('index'))
    else:
        flash('Failed to get access token.')
        return redirect(url_for('index'))

@app.route('/add_script_tag', methods=['POST'])
def add_script_tag():
    global access_token
    script_src = request.form.get('script_src')
    if not script_src:
        flash('Script URL is required.')
        return redirect(url_for('index'))
    
    url = f"https://{shop}/admin/api/2024-07/script_tags.json"
    headers = {"X-Shopify-Access-Token": access_token}
    payload = {
        "script_tag": {
            "event": "onload",
            "src": script_src
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        flash('ScriptTag added successfully.')
    else:
        flash(f'Failed to add ScriptTag: {response.json().get("errors", "Unknown error")}')
    return redirect(url_for('index'))

@app.route('/delete_script_tag/<int:script_id>', methods=['POST'])
def delete_script_tag(script_id):
    global access_token
    url = f"https://{shop}/admin/api/2024-07/script_tags/{script_id}.json"
    headers = {"X-Shopify-Access-Token": access_token}
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        flash('ScriptTag deleted successfully.')
    else:
        flash(f'Failed to delete ScriptTag: {response.json().get("errors", "Unknown error")}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)
