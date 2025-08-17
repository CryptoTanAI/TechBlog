import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    def __init__(self):
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.email = os.getenv('EMAIL_ADDRESS')
        self.password = os.getenv('EMAIL_PASSWORD')
    
    def send_welcome_email(self, subscriber_email):
        try:
            if not self.email or not self.password:
                print("Email credentials not configured")
                return False
                
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = subscriber_email
            msg['Subject'] = "Welcome to TechSouth Weekly!"
            
            body = """
Welcome to TechSouth Weekly!

Thank you for subscribing to our newsletter. You'll now receive:

• Weekly insights on Global South technology trends
• Exclusive research reports and analysis
• Case studies from successful tech implementations
• Policy updates and their implications

You can unsubscribe at any time by replying to any newsletter.

Best regards,
The TechSouth Team

---
TechSouth - Empowering the Global South through Technology
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            print(f"Welcome email sent to {subscriber_email}")
            return True
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
            return False
