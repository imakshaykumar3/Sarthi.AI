import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import markdown # Make sure to run: pip install markdown

def send_dummy_tickets(receiver_email: str, itinerary_md: str, bill_md: str):
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")

    if not sender_email or not sender_password:
        print("⚠️ SMTP credentials missing in .env")
        return False

    # Convert Markdown to HTML for a pretty email
    itinerary_html = markdown.markdown(itinerary_md)
    bill_html = markdown.markdown(bill_md, extensions=['tables'])

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "✈️ Your TravelGenie Itinerary & Tickets"
    msg['From'] = f"TravelGenie <{sender_email}>"
    msg['To'] = receiver_email

    # Email Template
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #334155; line-height: 1.6; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #2563eb; padding: 20px; text-align: center; color: white; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0;">Your Trip is Confirmed! 🌴</h1>
        </div>
        <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 10px 10px;">
            <p>Hello Traveler,</p>
            <p>Here are your dummy tickets and final bill details, curated specially by <b>TravelGenie</b>.</p>
            
            <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
                <h3 style="color: #2563eb; margin-top: 0;">🧾 Final Bill</h3>
                {bill_html}
            </div>

            <h3 style="color: #2563eb; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">📍 Your Itinerary</h3>
            <div>
                {itinerary_html}
            </div>
            
            <p style="margin-top: 30px;">Safe travels,<br><b>TravelGenie Team 🧞‍♂️</b></p>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html'))

    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False