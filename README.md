# Secure Role-Based Access Control (RBAC) Web Application

## Overview
This project is a **comprehensive security-focused web application** that implements **Role-Based Access Control (RBAC)** to efficiently manage **user authentication, permissions, and security policies**. Built with **Flask (backend) and React (frontend)**, it enforces **granular access control** to mitigate **unauthorized access, privilege escalation, and security threats**.

Designed with **enterprise-grade security principles**, the system integrates:
- **JWT-based authentication** for secure and scalable session management.
- **SQL Injection & XSS protection** through parameterized queries and robust input sanitization.
- **Multi-Factor Authentication (MFA)** and **account lockout mechanisms** to prevent unauthorized access attempts.
- **Secure file handling & validation** to guard against injection attacks and malicious uploads.
- **Granular RBAC policies** that enforce **least privilege access** based on user roles.
- **Comprehensive logging and monitoring** to track security-sensitive actions and potential threats.
- **Encrypted communications** using HTTPS and strict CORS policies for data integrity and confidentiality.

This project is designed for **organizations and security professionals** who need **a scalable, auditable, and security-hardened access control system**.

---

## 🔐 **Security Features**  
This application is built with **industry-standard security measures**, including:
- **Strong Password Policies & Hashing** (`bcrypt`, JWT, session-based security)
- **SQL Injection & Input Validation Protections** (ORM, parameterized queries, and sanitization)
- **Cross-Site Request Forgery (CSRF) Protection**
- **Two-Factor Authentication (2FA) & Secure Token Expiry Mechanisms**
- **Account Lockout Mechanism** (Brute-force attack prevention)
- **Role-Based Access Control (RBAC) with Granular Permissions**
- **Real-Time Logging & Threat Monitoring**
- **Secure HTTPS Enforcement & TLS Encryption for Data in Transit**
- **Session Management & Token Expiry Handling**

This system ensures a **robust, attack-resistant environment** by continuously validating user actions, implementing proactive threat detection, and enforcing **best security practices** across all interactions.

---


## 🎥 **Demo Videos**
- 📌 **[Security Demo](Security%20Demo.mp4)** – Highlights the **security mechanisms** in place, including **RBAC implementation, authentication flow, and security code features**.
- 📌 **[Web App Demo](Web%20App%20Demo.mp4)** – Showcases the **general functionality and GUI** of the web application.

---

## 📂 **Project Structure**
```
/secure-ecommerce-website
│── backend/             # Flask-based backend (RBAC logic, APIs, authentication)
│── frontend/            # React-based frontend (user interface, authentication flow)
├── Threat Modeling.docx   # Threat modeling and security assessment
├── Group_Two_503M_GCS_Report.docx  # Security implementation details
├── RBAC Diagram.pdf  # RBAC architecture diagram
│── Security Demo.mp4     # Security-focused application demo
│── Web App Demo.mp4      # GUI walkthrough and application features
│── README.md             # Main project documentation
```

---

## 🛠 **Tech Stack**
- **Backend:** Flask (Python), JWT, SQLAlchemy (MySQL)
- **Frontend:** React, Axios, Redux
- **Security Modules:** `bcrypt`, `Flask-Talisman` (HTTPS enforcement), CSRF protection

---

## 🔧 **Setup Instructions**

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/sargonradiyeh/Secure-Ecommerce-Website.git
cd rbac-web-app
```

### 2️⃣ Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3️⃣ Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

### 4️⃣ Configure Environment Variables
- Modify `.env` files for **backend and frontend** configurations.
- Set **database credentials, JWT secret keys, and HTTPS configurations**.

### 5️⃣ Run the Backend Server
```bash
cd backend
python app.py
```

### 6️⃣ Run the Frontend
```bash
cd ../frontend
npm start
```

---

## 🔍 **Threat Modeling & Security Analysis**
A comprehensive **threat model** was conducted to identify **attack vectors and mitigations**. This includes **STRIDE-based analysis**, security **countermeasures**, and **RBAC enforcement strategies**.

- 📄 **[Threat Model Report](Threat%20Modeling.docx)**
- 📄 **[Detailed Overall Report](Group_Two_503M_GCS_Report.docx)**
- 📜 **[RBAC Diagram](RBAC%20Diagram.pdf)** (Role-Permission Structure)

---

## 🎯 **Security-Oriented Design**
This project is **tailored for security professionals** looking to:
- **Strengthen identity & access management (IAM) practices.**
- **Implement RBAC for web applications.**
- **Enhance security with authentication & authorization policies.**

---
