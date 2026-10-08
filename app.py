from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# ===== SAMPLE DATA - This will become your real database =====
inventory = [
    {"id": 1, "name": "A4 Paper", "category": "Paper", "quantity": 35, "min_stock": 50, "price": 250, "unit": "Reams"},
    {"id": 2, "name": "Blue Pens", "category": "Writing", "quantity": 20, "min_stock": 30, "price": 10, "unit": "Pcs"},
    {"id": 3, "name": "Notebooks", "category": "Books", "quantity": 150, "min_stock": 20, "price": 40, "unit": "Pcs"},
    {"id": 4, "name": "Stapler", "category": "Office Tools", "quantity": 15, "min_stock": 10, "price": 150, "unit": "Pcs"},
    {"id": 5, "name": "Whiteboard Marker", "category": "Writing", "quantity": 8, "min_stock": 15, "price": 25, "unit": "Pcs"},
]

transactions = [
    {"id": 1, "item": "A4 Paper", "type": "Purchase", "quantity": 100, "date": "08-10-2026", "status": "Completed"},
    {"id": 2, "item": "Blue Pens", "type": "Issue", "quantity": 25, "date": "08-10-2026", "status": "Low Stock"},
    {"id": 3, "item": "Notebooks", "type": "Purchase", "quantity": 200, "date": "07-10-2026", "status": "Completed"},
]

def get_stats():
    total_items = len(inventory)
    available_stock = sum([i['quantity'] for i in inventory])
    low_stock = len([i for i in inventory if i['quantity'] <= i['min_stock']])
    total_cost = sum([i['quantity'] * i['price'] for i in inventory])
    return total_items, available_stock, low_stock, total_cost

@app.route("/")
def home():
    total_items, available_stock, low_stock, total_cost = get_stats()
    low_items = [i for i in inventory if i['quantity'] <= i['min_stock']]
    return render_template("dashboard.html", 
                           total_items=total_items,
                           available_stock=available_stock,
                           low_stock=low_stock,
                           total_cost=total_cost,
                           low_items=low_items,
                           transactions=transactions[:3],
                           inventory=inventory)

@app.route("/inventory")
def inventory_page():
    return render_template("inventory.html", inventory=inventory)

@app.route("/add_item", methods=["POST"])
def add_item():
    new_id = max([i['id'] for i in inventory]) + 1 if inventory else 1
    new_item = {
        "id": new_id,
        "name": request.form['name'],
        "category": request.form['category'],
        "quantity": int(request.form['quantity']),
        "min_stock": int(request.form['min_stock']),
        "price": int(request.form['price']),
        "unit": request.form['unit']
    }
    inventory.append(new_item)
    transactions.insert(0, {"id": len(transactions)+1, "item": new_item['name'], "type": "Purchase", "quantity": new_item['quantity'], "date": datetime.now().strftime("%d-%m-%Y"), "status": "Completed"})
    return redirect(url_for('inventory_page'))

@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    global inventory
    inventory = [i for i in inventory if i['id'] != item_id]
    return redirect(url_for('inventory_page'))

@app.route("/procurement", methods=["GET", "POST"])
def procurement():
    if request.method == "POST":
        item_id = int(request.form['item_id'])
        qty = int(request.form['qty'])
        for item in inventory:
            if item['id'] == item_id:
                item['quantity'] += qty
                transactions.insert(0, {"id": len(transactions)+1, "item": item['name'], "type": "Purchase", "quantity": qty, "date": datetime.now().strftime("%d-%m-%Y"), "status": "Completed"})
                break
        return redirect(url_for('procurement'))
    return render_template("procurement.html", inventory=inventory, transactions=transactions)

@app.route("/issue", methods=["GET", "POST"])
def issue_page():
    if request.method == "POST":
        item_id = int(request.form['item_id'])
        qty = int(request.form['qty'])
        for item in inventory:
            if item['id'] == item_id:
                if item['quantity'] >= qty:
                    item['quantity'] -= qty
                    status = "Low Stock" if item['quantity'] <= item['min_stock'] else "Issued"
                    transactions.insert(0, {"id": len(transactions)+1, "item": item['name'], "type": "Issue", "quantity": qty, "date": datetime.now().strftime("%d-%m-%Y"), "status": status})
                break
        return redirect(url_for('issue_page'))
    return render_template("issue.html", inventory=inventory, transactions=transactions)

@app.route("/analytics")
def analytics():
    return render_template("analytics.html", inventory=inventory)

@app.route("/alerts")
def alerts_page():
    low_items = [i for i in inventory if i['quantity'] <= i['min_stock']]
    return render_template("alerts.html", low_items=low_items, inventory=inventory)

@app.route("/history")
def history_page():
    return render_template("history.html", transactions=transactions)

if __name__ == "__main__":
    app.run(debug=True)