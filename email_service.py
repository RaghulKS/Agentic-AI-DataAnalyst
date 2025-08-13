import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import config

class EmailService:
    def __init__(self):
        self.smtp_server = getattr(config, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(config, 'SMTP_PORT', 587)
        self.email_user = getattr(config, 'EMAIL_USER', '')
        self.email_password = getattr(config, 'EMAIL_PASSWORD', '')
    
    def send_analysis_report(self, recipient_email, reports_dir, dataset_name="Unknown"):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = recipient_email
            msg['Subject'] = f"AutoAnalyst Report - {dataset_name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            body = f"""
            Dear User,
            
            Please find attached the analysis report for your dataset: {dataset_name}
            
            Analysis completed on: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}
            
            The report includes:
            - Comprehensive data analysis
            - Statistical insights
            - Visualizations
            - Recommendations
            
            Best regards,
            AutoAnalyst Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            if os.path.exists(reports_dir):
                for filename in os.listdir(reports_dir):
                    if filename.endswith('.pdf'):
                        filepath = os.path.join(reports_dir, filename)
                        self._attach_file(msg, filepath)
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, recipient_email, text)
            server.quit()
            
            return True, "Email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def _attach_file(self, msg, filepath):
        with open(filepath, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(filepath)}'
        )
        msg.attach(part)
    
    def send_notification(self, recipient_email, subject, message):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, recipient_email, text)
            server.quit()
            
            return True, "Notification sent successfully"
            
        except Exception as e:
            return False, f"Failed to send notification: {str(e)}"

def send_analysis_report(recipient_email, reports_dir, dataset_name="Unknown"):
    email_service = EmailService()
    return email_service.send_analysis_report(recipient_email, reports_dir, dataset_name)

def send_notification(recipient_email, subject, message):
    email_service = EmailService()
    return email_service.send_notification(recipient_email, subject, message)