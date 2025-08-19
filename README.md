Of course\! Here is a comprehensive `README.md` file for your GitHub repository. It explains what the project does, its key security features, and provides clear, step-by-step instructions for setup and deployment.

-----

# Secure Vault 🔐

Secure Vault is a multi-user, end-to-end encrypted file storage and sharing application built with Streamlit and PostgreSQL. It provides a secure environment where users can upload sensitive documents, manage them in a personal "wallet," and share them with other users without the server ever having access to the plaintext file content or the user's private encryption keys.

-----

## ✨ Core Features

  * **🔒 End-to-End Encryption:** Files are encrypted in the browser before upload using **AES-256-GCM**, ensuring tamper-proof and confidential storage.
  * **🔑 Two-Tier Key Management:** A central **Master Key** wraps (encrypts) each user's file-specific AES key. The database only ever stores these wrapped keys, never plaintext keys.
  * **🛡️ Multi-Factor Authentication (MFA):** All logins are secured with a one-time password (OTP) sent to the user's registered email address.
  * **👤 Secure User Management:** Includes user registration, password hashing (SHA-256), and secure password reset/username recovery flows via email OTP.
  * **🤝 Encrypted File Sharing:** Users can securely share files with others. The recipient receives the same wrapped AES key, allowing them to decrypt the file without compromising the original owner's key.
  * **📊 Audit Logging:** All critical user actions (login, upload, download, share, delete) are logged for security and compliance. Users can view their own activity history.
  * **🚀 Modern UI:** A clean, responsive interface with search functionality, progress bars for uploads, and toast notifications for a smooth user experience.
  * **⚙️ Secrets Management:** All sensitive credentials (database, master key, email server) are managed externally using Streamlit's built-in `secrets.toml`.

-----

## 🛠️ Tech Stack

  * **Frontend:** [Streamlit](https://streamlit.io/)
  * **Backend:** Python
  * **Database:** [PostgreSQL](https://www.postgresql.org/)
  * **Cryptography:** [PyCryptodome](https://www.pycryptodome.org/) (for AES-256-GCM)
  * **Database Driver:** [psycopg2-binary](https://www.psycopg.org/docs/)

-----

## 📂 Project Structure

```
secure-vault/
├── .streamlit/
│   └── secrets.toml        # Stores all credentials (DB, Master Key, SMTP)
├── uploads/
│   └── .gitkeep            # Directory for storing encrypted files
├── app.py                  # Main Streamlit application UI and logic
├── db.py                   # Database connection and query functions
├── encryptor.py            # Handles file encryption/decryption (AES-GCM)
├── key_manager.py          # Wraps/unwraps user AES keys with the Master Key
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

-----

## 🚀 Getting Started

Follow these steps to set up and run the Secure Vault application locally.

### 1\. Prerequisites

  * Python 3.8+
  * PostgreSQL server installed and running.

### 2\. Clone the Repository

```bash
git clone https://github.com/your-username/secure-vault.git
cd secure-vault
```

### 3\. Set Up a Python Virtual Environment

It's highly recommended to use a virtual environment.

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4\. Install Dependencies

Install all the required Python libraries from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5\. Configure the PostgreSQL Database

1.  Connect to your PostgreSQL instance (e.g., using `psql` or a GUI tool like pgAdmin).

2.  Create a new database and a user for the application.

    ```sql
    CREATE DATABASE secureshare;
    CREATE USER myuser WITH PASSWORD 'mypassword';
    GRANT ALL PRIVILEGES ON DATABASE secureshare TO myuser;
    ```

3.  Connect to the new database and run the schema setup script provided below to create the necessary tables.

    ```sql
    -- Connect to the secureshare database before running this
    \c secureshare

    -- 1) Users Table
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      username VARCHAR(50) NOT NULL UNIQUE,
      email VARCHAR(120) NOT NULL UNIQUE,
      password VARCHAR(128) NOT NULL,
      created_at TIMESTAMPTZ DEFAULT NOW(),
      last_login TIMESTAMPTZ NULL
    );

    -- 2) Files Table
    CREATE TABLE IF NOT EXISTS files (
      id SERIAL PRIMARY KEY,
      filename VARCHAR(255) NOT NULL,
      category VARCHAR(50) NOT NULL,
      owner VARCHAR(50) NOT NULL,
      upload_time TIMESTAMPTZ DEFAULT NOW(),
      aes_key BYTEA NOT NULL, -- Stores the WRAPPED user AES key
      FOREIGN KEY (owner) REFERENCES users(username) ON DELETE CASCADE
    );

    -- 3) Shared Files Table
    CREATE TABLE IF NOT EXISTS shared_files (
      id SERIAL PRIMARY KEY,
      file_id INT NOT NULL,
      shared_by VARCHAR(50) NOT NULL,
      shared_to VARCHAR(50) NOT NULL,
      aes_key BYTEA NOT NULL, -- Stores the WRAPPED user AES key
      shared_time TIMESTAMPTZ DEFAULT NOW(),
      FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
    );

    -- 4) Audit Logs Table
    CREATE TABLE IF NOT EXISTS audit_logs (
      id SERIAL PRIMARY KEY,
      username VARCHAR(50) NOT NULL,
      action VARCHAR(50) NOT NULL,
      filename VARCHAR(255) NULL,
      ip_address VARCHAR(45) NULL,
      ts TIMESTAMPTZ DEFAULT NOW()
    );
    ```

### 6\. Configure Application Secrets

1.  Create a directory named `.streamlit` in the root of your project folder.

2.  Inside `.streamlit`, create a file named `secrets.toml`.

3.  Copy the content below into `secrets.toml` and **replace the placeholder values** with your actual credentials.

    ```toml
    # .streamlit/secrets.toml

    [postgresql]
    host = "localhost"
    port = 5432
    database = "secureshare"      # Your DB name from step 5
    username = "myuser"           # Your DB user from step 5
    password = "mypassword"       # Your DB password from step 5

    [security]
    # IMPORTANT: Generate a strong, random 32-character string for this key
    # This key encrypts all user-specific keys. If you lose it, all data is lost.
    master_key = "your-very-strong-32-char-master-key"

    [email]
    # For using Gmail SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "your-email@gmail.com"
    # IMPORTANT: Use a Google App Password, not your regular login password.
    # See: https://support.google.com/accounts/answer/185833
    password = "your_google_app_password"
    from_name = "Secure Vault"
    from_email = "your-email@gmail.com"
    ```

### 7\. Run the Application

You are now ready to launch the Secure Vault\!

```bash
streamlit run app.py
```

Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

-----

## 🔐 Security Model Overview

The security of Secure Vault relies on a two-tier encryption architecture to ensure zero-knowledge storage.

1.  **File Encryption (Client-Side):**

      * When a user uploads a file, they provide a 16-character **User Key**.
      * This `User Key` is used to derive a 256-bit key that encrypts the file's contents using the **AES-GCM** algorithm.
      * AES-GCM is an authenticated encryption mode, meaning it not only encrypts the data but also generates a tag to protect its integrity. Any tampering with the encrypted file will cause decryption to fail.
      * The encrypted file (`nonce` + `tag` + `ciphertext`) is sent to the server.

2.  **Key Wrapping (Server-Side):**

      * The server receives the `User Key`. To store it securely, it cannot be saved in plaintext.
      * The `User Key` is encrypted (or "wrapped") using the application's global **Master Key** (stored in `secrets.toml`) and AES-GCM.
      * This "wrapped key" is what gets stored in the `files.aes_key` and `shared_files.aes_key` columns in the database.
      * **Crucially, the server only ever handles the `User Key` in memory for the brief moment it takes to wrap it. It is never stored at rest in its plaintext form.**

This model ensures that even if the database is compromised, attackers cannot decrypt user files without also having the **Master Key** from the `secrets.toml` file.

-----

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
