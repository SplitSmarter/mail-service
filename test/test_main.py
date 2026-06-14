import sys, os
# print(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.utils.mail_providers.elasticEmail import send_mail_elastic

def main():
    subject = "Test Email from Elastic"
    to = ["yourrecipient@example.com"]  # Replace with your test email
    html_content = "<h1>Hello!</h1><p>This is a <b>test email</b> from ElasticEmail.</p>"
    text_content = "Hello!\nThis is a test email from ElasticEmail."

    response = send_mail_elastic(
        subject=subject,
        to=to,
        html=html_content,
        text=text_content,
        from_email="no-reply@onewordmax.com",  # Use your verified sender
        from_name="Split Smart",
        cc=["optionalcc@example.com"],  # Or set to None
        bcc=["optionalbcc@example.com"]  # Or set to None
    )

    print("=== Email Send Result ===")
    print(response)

if __name__ == "__main__":
    main()
