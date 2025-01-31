import streamlit as st
import instaloader
import time
import smtplib
from email.message import EmailMessage

# Hardcoded username and password for demonstration
correct_username = "admin"
correct_password1 = "admin123"

# Email notification function
def send_email_notification(subject, body, sender_email, app_password, recipient_email):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)
        st.success("Email notification sent!")

# Monitor Instagram posts
def monitor_instagram_posts(usernames, sender_email, app_password, recipient_email):
    L = instaloader.Instaloader()
    for username in usernames:
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            st.write(f"Monitoring {username} for new posts...")

            posts = profile.get_posts()
            try:
                latest_post = next(posts)
                last_post_id = latest_post.shortcode
                st.write(f"Last post detected for {username}: https://www.instagram.com/p/{last_post_id}/")
            except StopIteration:
                st.write(f"No posts found for {username}")
                continue

            while True:
                try:
                    posts = profile.get_posts()
                    new_latest_post = next(posts)
                    new_post_id = new_latest_post.shortcode

                    if new_post_id != last_post_id:
                        post_url = f"https://www.instagram.com/p/{new_post_id}/"
                        st.success(f"New post detected for {username}! Post URL: {post_url}")
                        send_email_notification(
                            f"New Instagram Post Alert for {username}!",
                            f"Check the new post at {post_url}",
                            sender_email, app_password, recipient_email
                        )
                        last_post_id = new_post_id
                    else:
                        st.info(f"No new posts for {username}.")
                    time.sleep(300)
                except StopIteration:
                    st.error(f"Could not fetch posts for {username}.")
                    break
                except Exception as e:
                    st.error(f"Error monitoring {username}: {e}")
                    time.sleep(60)
        except Exception as e:
            st.error(f"Failed to load profile for {username}: {e}")

# Streamlit UI
st.title("Instagram Post Monitor")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.header("Login")
    username = st.text_input("Username")
    password1 = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == correct_username and password1 == correct_password1:
            st.session_state["authenticated"] = True
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid username or password!")
else:
    st.sidebar.success(f"Welcome, {correct_username}!")
    st.subheader("Instagram Monitoring Panel")

    usernames_input = st.text_input("Enter Instagram usernames (comma-separated)", "dailymail,bbcnews")
    usernames = [u.strip() for u in usernames_input.split(",")]

    sender_email = st.text_input("Sender Gmail", "your_email@gmail.com")
    app_password = st.text_input("Gmail App Password", "your_app_password", type="password")
    recipient_email = st.text_input("Recipient Email", "recipient_email@gmail.com")

    if st.button("Start Monitoring"):
        if usernames and sender_email and app_password and recipient_email:
            monitor_instagram_posts(usernames, sender_email, app_password, recipient_email)
        else:
            st.error("Please fill in all required fields.")
