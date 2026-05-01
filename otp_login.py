import re #For validating email with a regex pattern.
import random #For generating a numeric OTP.
import datetime #For tracking OTP creation time and expiry.
from zoneinfo import ZoneInfo
import smtplib #To send the OTP email using Gmail SMTP.
from email.message import EmailMessage
import hashlib #To securely store and compare the OTP as a hash.

class OtpVerification:
    def __init__(self, user_mail=None):
        self.user_mail = user_mail
        self.user_name = None
        self.hash_otp = None
        self.creation_time = None
        self.valid_limit = 5
        self.valid_upto_time = None
        self.no_of_attempts = 3
    def enryption(self,word):
        return hashlib.sha256(word.encode()).hexdigest()

    def mail_patt_ver(self):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.user_mail)

    def get_mail(self):  #Prompts the user to input their email and Validates it using a regex pattern and it Loops until a valid email is entered.
        while True:
            self.user_mail = input("Enter your email: ").strip()        
            if self.mail_patt_ver():
                print("Valid email address.")
                return
            else:
                print("Invalid email address. Please try again.")

    def get_username(self):  # Extracts username from the email address Takes the part before @ and remove numbers,_,.
        name = re.sub(r'\d+', '', self.user_mail.split("@")[0])
        self.user_name = ' '.join(word.capitalize() for word in re.split(r'[._\s]+', name) if word)

    def get_otp(self, otp_size=6): #generats 6 digit otp and encrypts using SHA_256 AND stores otp validity
        otp = ''.join([str(random.randint(0, 9)) for _ in range(otp_size)])
        self.creation_time = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
        self.valid_upto_time = self.creation_time + datetime.timedelta(minutes=self.valid_limit)
        self.hash_otp = self.enryption(otp)
        return otp

    def send_otp_email(self):  #here using smtp protocal sends a secure mail
        try:
            sender_email = "ksnksatwik07@gmail.com"
            sender_password = "pkyw oyhh gvrd wjss"
            msg = EmailMessage()
            msg.set_content(f"Dear {self.user_name},\n\nYour OTP is '{self.get_otp()}' , valid upto {self.valid_upto_time.strftime('%Y-%m-%d %H:%M:%S %Z')}.\n\nPlease do not share this code with anyone.")
            msg["Subject"] = "OTP Verification Code"
            msg["From"] = sender_email
            msg["To"] = self.user_mail

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)

            print("OTP has been sent to your email.")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def verify_otp(self): # Asks the user to enter the OTP: Checks if it's within the valid time,Compares hashed input to stored hash,Limits to 3 attempts,Returns "success", "timeout", or "failure"

        for i in range(self.no_of_attempts):
            if datetime.datetime.now(ZoneInfo("Asia/Kolkata")) > self.valid_upto_time:
                print("OTP has expired.")
                return "timeout"
            user_input = input("Enter your OTP: ").strip()
            if self.enryption(user_input) == self.hash_otp:
                return "success"
            else:
                print(f"Invalid OTP. {self.no_of_attempts - i - 1} attempt(s) left.")
        print("Too many incorrect attempts. Access denied.")
        return "failure"

    def home(self): #Displays a welcome message if OTP is successfully verified.
        print(f"\n{'-'*30}\n   Welcome, {self.user_name}\n{'-'*30}\n")

    def run(self):
        self.get_mail()
        self.get_username()

        while True:
            if not self.send_otp_email():
                print("Could not send OTP. Exiting.")
                return

            result = self.verify_otp()
            if result == "success":
                self.home()
                break
            elif result == "timeout":
                print("Resending a new OTP due to timeout...\n")
                continue
            elif result == "failure":
                print("Too many incorrect attempts. Access denied.")
                break

if __name__ == "__main__":
    otp = OtpVerification()
    otp.run()
