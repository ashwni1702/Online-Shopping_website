from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import stripe
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
EMAIL =  os.environ.get('EMAIL_ID')
PASSWORD =  os.environ.get('PASSWORD')
RECIPIENT_EMAIL = os.environ.get('SENDER_EMAIL')
# Initialize Stripe with your Stripe API Key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
publishable_api_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')

# Sample course data (you can use a database for real data)
courses = [
    {
        'id': 1,
        'name': 'Python',
        'price': 1999,  # Price in cents
    },
    {
        'id': 2,
        'name': 'Physics',
        'price': 2499,
    },
    {
        'id': 3,
        'name': 'Mathematics',
        'price': 1799,
    },
    {
        'id': 4,
        'name': 'Computational Fluid Dynamics',
        'price': 2999,
    },
]


@app.route('/')
def home():
    return render_template('index.html', courses=courses)


@app.route('/purchase/<int:course_id>', methods=['POST'])
def purchase(course_id):
    course = next((c for c in courses if c['id'] == course_id), None)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    try:
        # Create a Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': course['name'],
                        },
                        'unit_amount': course['price'],
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost:5000/success',
            cancel_url='http://localhost:5000/cancel',
        )
        return jsonify({'session_id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/FAQs")
def freq_asked_ques():
    return render_template("FAQs.html")


@app.route("/hiring", methods=['GET', 'POST'])
def hiring():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_no = request.form['number']
        resume = request.form['resume']
        skill = request.form['skill']
        # Create a MIME object for the email
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = "Recruitment Drive"

        # Attach the message body
        message_body = f"The candidate name: {name}, phone: {phone_no}, email: {email}, skill: {skill}"
        msg.attach(MIMEText(message_body, "plain"))

        # Establish a secure SMTP connection
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()

            try:
                # Login using your email and password
                connection.login(user=EMAIL, password=PASSWORD)

                # Send the email
                connection.sendmail(EMAIL, RECIPIENT_EMAIL, msg.as_string())

                print("Email sent successfully!")
            except smtplib.SMTPAuthenticationError as e:
                print(f"SMTP Authentication Error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

        flash("Your resume has been sent. you will be contacted shortly.")
        return redirect(url_for("home"))
    return render_template("work-with-us.html")


if __name__ == '__main__':
    app.run(debug=True)
