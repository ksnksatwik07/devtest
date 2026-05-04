import re
import os
import secrets
import hashlib
import datetime
import smtplib
from email.message import EmailMessage
from zoneinfo import ZoneInfo


# ==============================
# 🔐 OTP SERVICE
# ==============================
class OTPService:
    def __init__(self, expiry_minutes=5, otp_length=6):
        self.expiry_minutes = expiry_minutes
        self.otp_length = otp_length
        self.hashed_otp = None
        self.expiry_time = None
        self.tz = ZoneInfo("Asia/Kolkata")

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def generate_otp(self) -> str:
        otp = ''.join(secrets.choice("0123456789") for _ in range(self.otp_length))
        self.hashed_otp = self._hash(otp)
        self.expiry_time = datetime.datetime.now(self.tz) + datetime.timedelta(minutes=self.expiry_minutes)
        return otp

    def is_expired(self) -> bool:
        return datetime.datetime.now(self.tz) > self.expiry_time

    def verify(self, user_input: str) -> bool:
        return self._hash(user_input) == self.hashed_otp


# ==============================
# 📧 EMAIL SERVICE
# ==============================
class EmailService:
    def __init__(self):
        self.sender_email = "ksnksatwik07@gmail.com"
        self.sender_password = "pkyw oyhh gvrd wjss"

    def send_otp(self, receiver_email: str, username: str, otp: str, expiry_time):
        if not self.sender_email or not self.sender_password:
            print("❌ Email credentials not set in environment variables.")
            return False

        try:
            msg = EmailMessage()
            msg["Subject"] = "Your OTP Code"
            msg["From"] = self.sender_email
            msg["To"] = receiver_email

            msg.add_alternative(f"""
            <html>
                <body>
                    <h3>Hello {username},</h3>
                    <p>Your OTP is: <b>{otp}</b></p>
                    <p>Valid until: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><i>Do not share this code with anyone.</i></p>
                </body>
            </html>
            """, subtype='html')

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.sender_email, self.sender_password)
                smtp.send_message(msg)

            print("✅ OTP sent successfully.")
            return True

        except smtplib.SMTPAuthenticationError:
            print("❌ Authentication failed. Check email credentials.")
        except smtplib.SMTPException as e:
            print("❌ SMTP error:", e)

        return False


# ==============================
# 👤 USER SERVICE
# ==============================
class UserService:
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def get_email(self) -> str:
        while True:
            email = input("Enter your email: ").strip()
            if re.match(self.EMAIL_REGEX, email):
                return email
            print("❌ Invalid email. Try again.")

    def extract_username(self, email: str) -> str:
        name_part = re.sub(r'\d+', '', email.split("@")[0])
        return ' '.join(word.capitalize() for word in re.split(r'[._\s]+', name_part) if word)


# ==============================
# 🎯 MAIN APPLICATION
# ==============================
class OTPApplication:
    def __init__(self):
        self.user_service = UserService()
        self.otp_service = OTPService()
        self.email_service = EmailService()

        self.max_attempts = 3
        self.max_resends = 3

    def run(self):
        email = self.user_service.get_email()
        username = self.user_service.extract_username(email)

        resend_count = 0

        while resend_count < self.max_resends:
            otp = self.otp_service.generate_otp()

            if not self.email_service.send_otp(
                email, username, otp, self.otp_service.expiry_time
            ):
                print("Exiting due to email failure.")
                return

            if self.verify_flow():
                print(f"\n🎉 Welcome, {username}!")
                return

            resend_count += 1
            print(f"🔁 Resending OTP... ({resend_count}/{self.max_resends})\n")

        print("❌ Too many failed attempts. Try again later.")

    def verify_flow(self) -> bool:
        for attempt in range(self.max_attempts):
            if self.otp_service.is_expired():
                print("⏳ OTP expired.")
                return False

            user_input = input("Enter OTP: ").strip()

            if not user_input.isdigit() or len(user_input) != 6:
                print("❌ Invalid format. Enter 6-digit OTP.")
                continue

            if self.otp_service.verify(user_input):
                return True

            print(f"❌ Incorrect OTP. {self.max_attempts - attempt - 1} attempts left.")

        return False


# ==============================
# 🚀 ENTRY POINT
# ==============================
if __name__ == "__main__":
    app = OTPApplication()
    app.run()