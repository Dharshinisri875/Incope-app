from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary storage for data (in-memory, reset when server restarts)
branch_data = []
num_branches = 0

@app.route('/', methods=['GET', 'POST'])
def index():
    global num_branches, branch_data
    if request.method == 'POST':
        try:
            num_branches = int(request.form['num_branches'])
            if num_branches <= 0:
                raise ValueError
        except ValueError:
            return render_template('index.html', error="Enter a valid positive number.")
        branch_data = []
        return redirect(url_for('branches'))
    return render_template('index.html')


@app.route('/branches', methods=['GET', 'POST'])
def branches():
    global num_branches, branch_data
    if request.method == 'POST':
        branch_name = request.form['branch_name'].strip()
        swiggy = request.form['swiggy']
        zomato = request.form['zomato']

        if not branch_name.isidentifier():
            error = "Branch name must be a valid identifier (letters, digits, underscores, no spaces)."
            return render_template('branches.html', current=len(branch_data)+1, total=num_branches, error=error)

        try:
            swiggy = int(swiggy)
            zomato = int(zomato)
            if swiggy < 0 or zomato < 0:
                raise ValueError
        except ValueError:
            error = "Swiggy and Zomato must be non-negative integers."
            return render_template('branches.html', current=len(branch_data)+1, total=num_branches, error=error)

        branch_data.append({'name': branch_name, 'swiggy': swiggy, 'zomato': zomato})

        if len(branch_data) == num_branches:
            return redirect(url_for('common'))
        else:
            return redirect(url_for('branches'))

    return render_template('branches.html', current=len(branch_data)+1, total=num_branches)

@app.route('/common', methods=['GET', 'POST'])
def common():
    global branch_data
    if request.method == 'POST':
        try:
            dine_in = int(request.form['dine_in'])
            pick_up = int(request.form['pick_up'])
            delivery = int(request.form['delivery'])
            if dine_in < 0 or pick_up < 0 or delivery < 0:
                raise ValueError
        except ValueError:
            return render_template('common.html', error="Enter valid non-negative integers.")

        # Calculate deducted swiggy and zomato for each branch
        for b in branch_data:
            b['swiggy_deducted'] = b['swiggy'] * 0.7
            b['zomato_deducted'] = b['zomato'] * 0.7
            b['deducted_sum'] = b['swiggy_deducted'] + b['zomato_deducted']


        # Sum deducted swiggy and zomato individually across branches
        total_swiggy_deducted = sum(b['swiggy_deducted'] for b in branch_data)
        total_zomato_deducted = sum(b['zomato_deducted'] for b in branch_data)

        # Common sales total
        common_total = dine_in + pick_up + delivery

        app.config['common_total'] = common_total

        # Grand total = deducted swiggy + deducted zomato + common total
        grand_total = total_swiggy_deducted + total_zomato_deducted + common_total

        return render_template('result.html',
                               branches=branch_data,
                               total_swiggy_deducted=total_swiggy_deducted,
                               total_zomato_deducted=total_zomato_deducted,
                               common_total=common_total,
                               grand_total=grand_total)

    return render_template('common.html')

@app.route('/bills', methods=['GET', 'POST'])
def bills():
    global branch_data
    if request.method == 'POST':
        try:
            num_bills = int(request.form['num_bills'])
            if num_bills <= 0:
                raise ValueError
        except ValueError:
            return render_template('bills.html', error="Enter a valid positive number.")

        return redirect(url_for('enter_bills', num_bills=num_bills))

    return render_template('bills.html')

@app.route('/enter_bills/<int:num_bills>', methods=['GET', 'POST'])
def enter_bills(num_bills):
    global branch_data

    # Retrieve stored common_total
    common_total = app.config.get('common_total', 0)

    total_swiggy_deducted = sum(b['swiggy_deducted'] for b in branch_data)
    total_zomato_deducted = sum(b['zomato_deducted'] for b in branch_data)
    grand_total = total_swiggy_deducted + total_zomato_deducted + common_total

    if request.method == 'POST':
        bill_inputs = []
        total_bills_value = 0

        for i in range(1, num_bills + 1):
            try:
                value = float(request.form[f'bill_{i}'])
                if value < 0:
                    raise ValueError
                bill_inputs.append(value)
                total_bills_value += value
            except ValueError:
                return render_template('enter_bills.html', num_bills=num_bills, error="Enter valid positive amounts.")

        # Redirect to enter_cost after POST
        return redirect(url_for('enter_cost',
                                grand_total=grand_total,
                                total_bills_value=total_bills_value))

    return render_template('enter_bills.html', num_bills=num_bills)

@app.route('/enter_cost', methods=['GET', 'POST'])
def enter_cost():
    grand_total = float(request.args.get('grand_total'))
    total_bills_value = float(request.args.get('total_bills_value'))

    fixed_costs = {
        'water_bill': 200,
        'gas_bill': 667,
        'eb_bill': 350,
        'rent': 1334,
        'veg_section': 3000,
        'non_veg_section': 3810,
        'sweet': 240,
        'oil': 450,
        'ghee': 200
    }

    if request.method == 'POST':
        try:
            mutton_cost = float(request.form['mutton_cost'])
            egg_cost = float(request.form['egg_cost'])
            parotta_cost = float(request.form['parotta_cost'])
            chappathi_dough_cost = float(request.form['chappathi_dough_cost'])
            packing_cost = float(request.form['packing_cost'])
            labour_cost = float(request.form['labour_cost'])
            ad_cost = float(request.form['ad_cost'])

            if any(cost < 0 for cost in [
                mutton_cost, egg_cost, parotta_cost, chappathi_dough_cost,
                packing_cost, labour_cost, ad_cost]):
                raise ValueError

        except ValueError:
            return render_template('enter_cost.html',
                                   grand_total=grand_total,
                                   total_bills_value=total_bills_value,
                                   fixed_costs=fixed_costs,      # <-- pass fixed_costs here
                                   error="Enter valid positive values for all costs.")

        total_fixed_cost = sum(fixed_costs.values())
        total_entered_costs = (mutton_cost + egg_cost + parotta_cost +
                               chappathi_dough_cost + packing_cost +
                               labour_cost + ad_cost)

        total_costs = total_fixed_cost + total_entered_costs + total_bills_value

        final_income = grand_total - total_costs

        return render_template('final_result.html',
                               grand_total=grand_total,
                               total_bills_value=total_bills_value,
                               fixed_costs=fixed_costs,
                               mutton_cost=mutton_cost,
                               egg_cost=egg_cost,
                               parotta_cost=parotta_cost,
                               chappathi_dough_cost=chappathi_dough_cost,
                               packing_cost=packing_cost,
                               labour_cost=labour_cost,
                               ad_cost=ad_cost,
                               total_costs=total_costs,
                               final_income=final_income)

    # On GET request, also pass fixed_costs
    return render_template('enter_cost.html',
                           grand_total=grand_total,
                           total_bills_value=total_bills_value,
                           fixed_costs=fixed_costs)  # <-- pass fixed_costs here too



import pymysql
from datetime import date
today = date.today()



# MySQL connection setup
def get_connection():
    return pymysql.connect(host='localhost',
                           user='root',
                           password='password123',
                           db='xpenzo',
                           cursorclass=pymysql.cursors.DictCursor)




# Save final income in database
@app.route('/save_income', methods=['POST'])
def save_income():
    final_income = float(request.form['final_income'])
    income_date = request.form['income_date']
    grand_total = float(request.form['grand_total'])
    total_bills_value = float(request.form['total_bills_value'])

    fixed_costs = {
        'water_bill': 200,
        'gas_bill': 667,
        'eb_bill': 350,
        'rent': 1334,
        'veg_section': 3000,
        'non_veg_section': 3810,
        'sweet': 240,
        'oil': 450,
        'ghee': 200
    }

    mutton_cost = float(request.form['mutton_cost'])
    egg_cost = float(request.form['egg_cost'])
    parotta_cost = float(request.form['parotta_cost'])
    chappathi_dough_cost = float(request.form['chappathi_dough_cost'])
    packing_cost = float(request.form['packing_cost'])
    labour_cost = float(request.form['labour_cost'])
    ad_cost = float(request.form['ad_cost'])

    total_fixed_cost = sum(fixed_costs.values())
    total_entered_costs = (
        mutton_cost + egg_cost + parotta_cost +
        chappathi_dough_cost + packing_cost + labour_cost + ad_cost
    )
    total_costs = total_fixed_cost + total_entered_costs + total_bills_value

    # Save to DB
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO income_records (date, income) VALUES (%s, %s)",
            (income_date, final_income)
        )
    conn.commit()
    conn.close()

    return render_template('final_result.html',
                           grand_total=grand_total,
                           total_bills_value=total_bills_value,
                           fixed_costs=fixed_costs,
                           mutton_cost=mutton_cost,
                           egg_cost=egg_cost,
                           parotta_cost=parotta_cost,
                           chappathi_dough_cost=chappathi_dough_cost,
                           packing_cost=packing_cost,
                           labour_cost=labour_cost,
                           ad_cost=ad_cost,
                           total_costs=total_costs,
                           final_income=final_income,
                           current_date=income_date,
                           saved=True)


# ✅ This route was missing (causing BuildError)
@app.route('/monthly')
def monthly_analysis():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT DATE_FORMAT(date, '%Y-%m') AS month, SUM(income) AS total_income
            FROM income_records
            GROUP BY month
            ORDER BY month
        """)
        results = cursor.fetchall()
    conn.close()

    months = [row['month'] for row in results]
    incomes = [float(row['total_income']) for row in results]

    return render_template('monthly.html', months=months, incomes=incomes, zip=zip)


# ✅ This must be at the very end!
if __name__ == '__main__':
    app.run(debug=True)
