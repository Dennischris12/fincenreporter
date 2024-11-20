from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, login_user
from app import app, db
from app.models import User, Filing
import stripe
from reportlab.pdfgen import canvas
import requests

# Function to check WordPress login
def check_wordpress_login():
    response = requests.get('https://your-wordpress-site.com/wp-json/myplugin/v1/check-login', cookies=request.cookies)
    data = response.json()

    if data.get('logged_in'):
        user_id = data['user_id']
        user = User.query.get(user_id)
        if user:
            login_user(user)

# Routes for User Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    filings = Filing.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', filings=filings)

# Admin Dashboard Route
@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    filings = Filing.query.all()
    return render_template('admin_dashboard.html', filings=filings)

# File BOI Route - Displays form and handles submission
@app.route('/file', methods=['POST', 'GET'])
@login_required
def file_boi():
    if request.method == 'POST':
        filing = Filing(
            user_id=current_user.id,
            filing_status="Pending",
            filing_date="2024-11-19",  # Modify to capture actual date
            company_name=request.form['company_name']
        )
        db.session.add(filing)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('file_form.html')

# New Filing Route - Handles file upload and filing data submission
@app.route('/new-filing', methods=['POST', 'GET'])
@login_required
def new_filing():
    if request.method == 'POST':
        company_name = request.form['company_name']
        id_upload = request.files['id_upload']
        file_path = f'static/uploads/{id_upload.filename}'
        id_upload.save(file_path)

        filing = Filing(
            user_id=current_user.id,
            filing_status="Pending",
            filing_date="2024-11-19",
            company_name=company_name
        )
        db.session.add(filing)
        db.session.commit()

        flash('Filing submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('new_filing.html')

# Stripe Payment Route
@app.route('/pay', methods=['POST'])
@login_required
def pay_filing():
    token = request.form['stripeToken']
    charge = stripe.Charge.create(
        amount=15000,  # $150 in cents
        currency='usd',
        description='BOI Filing',
        source=token,
    )
    return redirect(url_for('file_boi'))

# Review Route - Handles the Stripe review and payment confirmation
@app.route('/review', methods=['POST', 'GET'])
@login_required
def review():
    if request.method == 'POST':
        token = request.form['stripeToken']
        try:
            charge = stripe.Charge.create(
                amount=15000,  # Amount in cents ($150)
                currency='usd',
                description='BOI Filing Payment',
                source=token,
            )
            flash('Payment Successful', 'success')
        except stripe.error.StripeError as e:
            flash(f"Error: {e.user_message}", 'error')
        return redirect(url_for('file_boi'))
    return render_template('review.html')

# PDF Generation Function (Transcript)
def generate_pdf(filing_id):
    filing = Filing.query.get(filing_id)
    file_path = f'static/pdfs/{filing_id}_transcript.pdf'
    c = canvas.Canvas(file_path)
    c.drawString(100, 750, f"Filing Transcript for {filing.company_name}")
    c.drawString(100, 730, f"Status: {filing.filing_status}")
    c.save()

    # Update the filing record with the PDF path
    filing.transcript_pdf = file_path
    db.session.commit()
    return file_path

# Endpoint to download the transcript PDF
@app.route('/transcript/<filing_id>')
@login_required
def download_transcript(filing_id):
    filing = Filing.query.get_or_404(filing_id)
    return jsonify({'status': filing.filing_status, 'transcript': filing.transcript_pdf})


if __name__ == "__main__":
    app.run(debug=True)
