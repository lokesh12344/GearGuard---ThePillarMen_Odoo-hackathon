import streamlit as st
import sqlite3
import re
import bcrypt
from datetime import datetime
from pathlib import Path

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="GearGuard - Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================== CUSTOM CSS ==================
st.markdown("""
<style>
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .stContainer {
        padding: 20px;
    }
    
    .login-container {
        background: white;
        border-radius: 12px;
        padding: 40px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        margin-top: 50px;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .login-header h1 {
        color: #667eea;
        font-size: 32px;
        margin-bottom: 10px;
        font-weight: bold;
    }
    
    .login-header p {
        color: #666;
        font-size: 14px;
    }
    
    .error-message {
        background-color: #fee;
        color: #c33;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
        border-left: 4px solid #c33;
    }
    
    .success-message {
        background-color: #efe;
        color: #3c3;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
        border-left: 4px solid #3c3;
    }
    
    .info-message {
        background-color: #eef;
        color: #33c;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
        border-left: 4px solid #33c;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .input-label {
        color: #333;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .divider {
        text-align: center;
        color: #999;
        margin: 20px 0;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ================== DATABASE CONNECTION ==================
def get_database_path():
    """Get path to the SQLite database"""
    import os
    # Get the absolute path based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(script_dir), "Database", "maintenance_system.db")
    return db_path

@st.cache_resource
def get_database_connection():
    """Create and return database connection"""
    db_path = get_database_path()
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        return conn
    except Exception as e:
        return None

# ================== EMAIL VALIDATION ==================
def validate_email_format(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@gearguard\.com$'
    return re.match(pattern, email) is not None

def extract_valid_email_domain(email):
    """Extract and validate email domain"""
    if '@' not in email:
        return None
    domain = email.split('@')[1]
    return domain == 'gearguard.com'

# ================== PASSWORD HASHING ==================
def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except:
        return False

# ================== DATABASE OPERATIONS ==================
def get_employee_by_email(email):
    """Retrieve employee from database by email"""
    try:
        conn = get_database_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT employee_id, name, contact_email, password, department, designation FROM employee WHERE contact_email = ?",
            (email,)
        )
        result = cursor.fetchone()
        return result
    except Exception as e:
        return None

def authenticate_employee(email, password):
    """Authenticate employee credentials"""
    # Validate email format
    if not validate_email_format(email):
        return {
            'success': False,
            'message': '❌ Invalid email format. Please use your @gearguard.com email address.'
        }
    
    # Get employee from database
    employee = get_employee_by_email(email)
    
    if not employee:
        return {
            'success': False,
            'message': '❌ Email not found in the system. Please check your email address.'
        }
    
    employee_id, name, contact_email, stored_password, department, designation = employee
    
    # Verify password
    if verify_password(password, stored_password):
        return {
            'success': True,
            'message': f'✅ Welcome, {name}!',
            'employee_id': employee_id,
            'name': name,
            'email': contact_email,
            'department': department,
            'designation': designation
        }
    else:
        return {
            'success': False,
            'message': '❌ Invalid password. Please try again.'
        }

# ================== SESSION MANAGEMENT ==================
def initialize_session():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'employee_data' not in st.session_state:
        st.session_state.employee_data = None
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'locked_until' not in st.session_state:
        st.session_state.locked_until = None

def logout():
    """Logout the current user"""
    st.session_state.authenticated = False
    st.session_state.employee_data = None
    st.session_state.login_attempts = 0
    st.success("You have been logged out successfully.")

# ================== MAIN LOGIN PAGE ==================
def login_page():
    """Render the login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="login-header">
            <h1>🔐 GearGuard</h1>
            <p>Enterprise Maintenance Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if account is locked
        if st.session_state.locked_until and datetime.now() < st.session_state.locked_until:
            st.markdown("""
            <div class="error-message">
                🔒 Account temporarily locked due to multiple failed login attempts. 
                Please try again in a few minutes.
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Reset lock if time has passed
        if st.session_state.locked_until and datetime.now() >= st.session_state.locked_until:
            st.session_state.locked_until = None
            st.session_state.login_attempts = 0
        
        # Email input
        st.markdown('<label class="input-label">📧 Email Address</label>', unsafe_allow_html=True)
        email = st.text_input(
            "Email",
            value="",
            placeholder="your.name@gearguard.com",
            label_visibility="collapsed"
        )
        
        # Real-time email validation
        if email:
            if not validate_email_format(email):
                st.markdown("""
                <div class="info-message">
                    ⓘ Email must be in format: name@gearguard.com
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-message">
                    ✓ Valid email format
                </div>
                """, unsafe_allow_html=True)
        
        # Password input
        st.markdown('<label class="input-label">🔑 Password</label>', unsafe_allow_html=True)
        password = st.text_input(
            "Password",
            type="password",
            value="",
            placeholder="Enter your password",
            label_visibility="collapsed"
        )
        
        # Login button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 Login", use_container_width=True):
                if not email or not password:
                    st.markdown("""
                    <div class="error-message">
                        ❌ Please enter both email and password.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Attempt authentication
                    result = authenticate_employee(email, password)
                    
                    if result['success']:
                        st.session_state.authenticated = True
                        st.session_state.employee_data = {
                            'employee_id': result['employee_id'],
                            'name': result['name'],
                            'email': result['email'],
                            'department': result['department'],
                            'designation': result['designation'],
                            'login_time': datetime.now()
                        }
                        st.session_state.login_attempts = 0
                        st.markdown("""
                        <div class="success-message">
                            ✓ Login successful! Redirecting to dashboard...
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        import time
                        time.sleep(1)
                        # Redirect to main.py (the dashboard)
                        st.switch_page("pages/main.py")
                    else:
                        st.session_state.login_attempts += 1
                        remaining_attempts = 3 - st.session_state.login_attempts
                        
                        if st.session_state.login_attempts >= 3:
                            st.session_state.locked_until = datetime.now().replace(second=0, microsecond=0) + __import__('datetime').timedelta(minutes=5)
                            st.markdown("""
                            <div class="error-message">
                                🔒 Too many failed attempts. Account locked for 5 minutes.
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="error-message">
                                {result['message']}<br/>
                                <small>Attempts remaining: {remaining_attempts}</small>
                            </div>
                            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("ℹ️ Demo", use_container_width=True):
                st.markdown("""
                <div class="info-message">
                    <strong>Demo Credentials:</strong><br/>
                    Email: rajesh.kumar@gearguard.com<br/>
                    Password: gearguard123
                </div>
                """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div class="divider">
            🔒 Your login credentials are secure and encrypted
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ================== DASHBOARD PAGE ==================
def dashboard_page():
    """Render the dashboard page after login"""
    employee = st.session_state.employee_data
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h2>🔐 GearGuard</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: #f0f2f6; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p><strong>👤 {employee['name']}</strong></p>
            <p style="font-size: 12px; color: #666;">
                {employee['designation']}<br/>
                {employee['department']}
            </p>
            <p style="font-size: 12px; color: #999;">
                📧 {employee['email']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        st.markdown("### Navigation")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
        with col2:
            if st.button("🛠️ Maintenance", use_container_width=True):
                st.session_state.page = "maintenance"
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚙️ Equipment", use_container_width=True):
                st.session_state.page = "equipment"
        with col2:
            if st.button("👥 Team", use_container_width=True):
                st.session_state.page = "team"
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # Main content
    st.markdown(f"""
    <div style="padding: 20px;">
        <h1>Welcome, {employee['name']}! 👋</h1>
        <p>You are logged into the GearGuard Maintenance Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display employee information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Employee ID", employee['employee_id'])
    
    with col2:
        st.metric("Department", employee['department'])
    
    with col3:
        login_time = employee['login_time'].strftime("%H:%M:%S")
        st.metric("Login Time", login_time)
    
    st.divider()
    
    # Dashboard content placeholder
    st.info("📋 Dashboard content will be displayed here. You can navigate using the sidebar menu.")

# ================== MAIN APPLICATION ==================
def main():
    """Main application entry point"""
    initialize_session()
    
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    if st.session_state.authenticated:
        dashboard_page()
    else:
        login_page()

if __name__ == "__main__":
    main()
