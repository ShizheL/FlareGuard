from flask import Flask, request, jsonify, render_template
import main  # Import your script to calculate credibility

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        wallet_id = request.form.get("wallet-address")
        print(wallet_id)
        n1,n2,n3,count = get_credibility(wallet_id)
        return render_template('result.html', n1=n1, n2=n2,n3=n3,count=count)
    return render_template('index.html')

def get_credibility(wallet_address):    
    if not wallet_address:
        return "error: No wallet address", 0 #html of nice format
    
    n1,n2,n3,count = main.main(wallet_address)
    return n1,n2,n3,count #html of nice format

if __name__ == '__main__':
    app.run(debug=True)
