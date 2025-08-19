# db.py
import streamlit as st
import psycopg2                                      # <-- CHANGED
from psycopg2 import Error
from psycopg2.extras import DictCursor
from datetime import datetime

def connect_db():
    """Establish DB connection using secrets.toml"""
    try:
        # Assumes a [postgresql] section in your secrets.toml
        cfg = st.secrets["postgresql"]               # <-- CHANGED
        conn = psycopg2.connect(                     # <-- CHANGED
            host=cfg["host"],
            user=cfg["username"],
            password=cfg["password"],
            dbname=cfg["database"] # Note: param is 'dbname'
        )
        return conn
    except Error as e:
        st.error(f"❌ DB connection error: {e}")      # <-- CHANGED (shows error in UI)
        return None


# ==============================
# Logging & Audit (No changes needed here)
# ==============================
def log_action(username: str, action: str, filename: str | None = None, ip_address: str | None = None):
    conn = connect_db()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO audit_logs (username, action, filename, ip_address) VALUES (%s, %s, %s, %s)",
            (username, action, filename, ip_address)
        )
        conn.commit()
    finally:
        conn.close()


# ==============================
# User Management
# ==============================
def get_user_by_username(username: str):
    conn = connect_db()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=DictCursor) # <-- CHANGED
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        return cur.fetchone()
    finally:
        conn.close()


def get_user_by_email(email: str):
    conn = connect_db()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=DictCursor) # <-- CHANGED
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        return cur.fetchone()
    finally:
        conn.close()

def update_last_login(username: str):
    conn = connect_db()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET last_login=NOW() WHERE username=%s", (username,))
        conn.commit()
    finally:
        conn.close()


# ==============================
# OTP / MFA Support
# ==============================
def set_otp(username: str, code: str, expiry: datetime):
    conn = connect_db()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET otp_code=%s, otp_expiry=%s WHERE username=%s",
            (code, expiry, username)
        )
        conn.commit()
        return True
    finally:
        conn.close()


def verify_otp(username: str, code: str):
    conn = connect_db()
    if not conn:
        return False
    try:
        cur = conn.cursor(cursor_factory=DictCursor) # <-- CHANGED
        cur.execute("SELECT otp_code, otp_expiry FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        if row and row["otp_code"] == code and row["otp_expiry"] > datetime.now():
            return True
        return False
    finally:
        conn.close()

# ==============================
# Password Reset
# ==============================
def set_reset_token(email: str, token: str, expiry: datetime):
    conn = connect_db()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET reset_token=%s, reset_expiry=%s WHERE email=%s",
            (token, expiry, email)
        )
        conn.commit()
        return True
    finally:
        conn.close()


def verify_reset_token(token: str):
    conn = connect_db()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=DictCursor) # <-- CHANGED
        cur.execute("SELECT * FROM users WHERE reset_token=%s AND reset_expiry > NOW()", (token,))
        return cur.fetchone()
    finally:
        conn.close()

def update_password(email: str, new_hashed_pw: str):
    conn = connect_db()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET password=%s, reset_token=NULL, reset_expiry=NULL WHERE email=%s",
            (new_hashed_pw, email)
        )
        conn.commit()
        return True
    finally:
        conn.close()