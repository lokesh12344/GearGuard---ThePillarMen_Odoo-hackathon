import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from enum import Enum

# ================== CONFIGURATION ==================
st.set_page_config(
    page_title="GearGuard - Enterprise Maintenance Management",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== COLOR PALETTE ==================
COLORS = {
    'primary': '#5C6BC0',      # Indigo
    'secondary': '#42A5F5',    # Blue
    'accent': '#66BB6A',       # Green
    'warning': '#FFA726',      # Orange
    'danger': '#EF5350',       # Red
    'bg_light': '#F5F5F5',
    'bg_white': '#FFFFFF',
    'text_primary': '#212121',
    'text_secondary': "#FFFFFF",
    'border': '#E0E0E0'
}

# ================== CUSTOM CSS ==================
st.markdown("""
<style>
    :root {
        --primary: #5C6BC0;
        --secondary: #42A5F5;
        --accent: #66BB6A;
        --warning: #FFA726;
        --danger: #EF5350;
    }
    
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background: #FAFAFA;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-weight: 500;
        border-radius: 8px;
        padding: 12px 24px;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .card-header {
        font-size: 14px;
        color: #757575;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    
    .card-value {
        font-size: 32px;
        font-weight: 700;
        color: #212121;
        margin: 8px 0;
    }
    
    .card-subtext {
        font-size: 13px;
        color: #9E9E9E;
    }
    
    .health-badge-green {
        background: #E8F5E9;
        color: #2E7D32;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 12px;
    }
    
    .health-badge-yellow {
        background: #FFF3E0;
        color: #F57F17;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 12px;
    }
    
    .health-badge-red {
        background: #FFEBEE;
        color: #C62828;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 12px;
    }
    
    .priority-high {
        background: #FFEBEE;
        color: #C62828;
    }
    
    .priority-medium {
        background: #FFF3E0;
        color: #F57F17;
    }
    
    .priority-low {
        background: #E3F2FD;
        color: #1565C0;
    }
    
    .kanban-card {
        background: white;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #E0E0E0;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        border-left: 4px solid #5C6BC0;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .status-new {
        background: #E3F2FD;
        color: #0D47A1;
    }
    
    .status-inprogress {
        background: #FFF3E0;
        color: #E65100;
    }
    
    .status-repaired {
        background: #E8F5E9;
        color: #1B5E20;
    }
    
    .status-scrap {
        background: #FFEBEE;
        color: #B71C1C;
    }
    
    .divider {
        margin: 24px 0;
        border: 0;
        height: 1px;
        background: #E0E0E0;
    }
    
    .section-header {
        font-size: 24px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .subsection-header {
        font-size: 16px;
        font-weight: 600;
        color: #FFFFFF;
        margin-top: 20px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ================== SESSION STATE ==================
if 'role' not in st.session_state:
    st.session_state.role = 'Manager'

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

if 'selected_equipment' not in st.session_state:
    st.session_state.selected_equipment = None

if 'selected_request' not in st.session_state:
    st.session_state.selected_request = None

if 'task_running' not in st.session_state:
    st.session_state.task_running = False

# ================== SAMPLE DATA ==================
EQUIPMENT_DATA = pd.DataFrame({
    'Name': ['Injection Mold Press-A1', 'CNC Lathe-B2', 'Hydraulic Press-C3', 
             'Assembly Robot-D1', 'Conveyor Belt-E2', 'Welding Machine-F1'],
    'Serial No': ['EQ-2021-001', 'EQ-2021-002', 'EQ-2021-003', 
                  'EQ-2021-004', 'EQ-2021-005', 'EQ-2021-006'],
    'Department': ['Manufacturing', 'Manufacturing', 'Production', 
                   'Assembly', 'Logistics', 'Fabrication'],
    'Team': ['Team A', 'Team B', 'Team A', 'Team C', 'Team B', 'Team A'],
    'Warranty': ['Active', 'Active', 'Expired', 'Active', 'Expired', 'Active'],
    'Health': ['Good', 'Warning', 'Critical', 'Good', 'Fair', 'Good'],
    'Open Requests': [2, 5, 8, 1, 3, 2]
})

MAINTENANCE_REQUESTS = pd.DataFrame({
    'Request ID': ['MR-2025-001', 'MR-2025-002', 'MR-2025-003', 'MR-2025-004', 'MR-2025-005'],
    'Equipment': ['Injection Mold Press-A1', 'CNC Lathe-B2', 'Hydraulic Press-C3', 'Assembly Robot-D1', 'Conveyor Belt-E2'],
    'Category': ['Preventive', 'Corrective', 'Preventive', 'Corrective', 'Preventive'],
    'Priority': ['Medium', 'High', 'Critical', 'Low', 'Medium'],
    'Status': ['Open', 'In Progress', 'Open', 'Closed', 'Open'],
    'Created Date': [datetime.now() - timedelta(days=5), datetime.now() - timedelta(days=3),
                     datetime.now() - timedelta(days=10), datetime.now() - timedelta(days=1),
                     datetime.now() - timedelta(days=2)],
    'Assigned To': ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Williams', 'Tom Brown']
})

KANBAN_DATA = {
    'New': [
        {'id': 'K-001', 'subject': 'Oil change required', 'equipment': 'CNC Lathe-B2', 'priority': 'High', 'due': '2025-01-02', 'tech': 'JS', 'overdue': True, 'duration': '2h'},
        {'id': 'K-002', 'subject': 'Belt inspection', 'equipment': 'Conveyor Belt-E2', 'priority': 'Medium', 'due': '2025-01-05', 'tech': 'TB', 'overdue': False, 'duration': '1h'},
    ],
    'In Progress': [
        {'id': 'K-003', 'subject': 'Hydraulic seal replacement', 'equipment': 'Hydraulic Press-C3', 'priority': 'Critical', 'due': '2025-01-01', 'tech': 'MJ', 'overdue': True, 'duration': '4h'},
        {'id': 'K-004', 'subject': 'Calibration check', 'equipment': 'Injection Mold Press-A1', 'priority': 'Low', 'due': '2025-01-08', 'tech': 'JD', 'overdue': False, 'duration': '1.5h'},
    ],
    'Repaired': [
        {'id': 'K-005', 'subject': 'Motor replacement', 'equipment': 'Assembly Robot-D1', 'priority': 'High', 'due': '2024-12-25', 'tech': 'SW', 'overdue': False, 'duration': '3h'},
    ],
    'Scrap': [
        {'id': 'K-006', 'subject': 'Bearing assembly defective', 'equipment': 'CNC Lathe-B2', 'priority': 'Medium', 'due': '2024-12-20', 'tech': 'JD', 'overdue': False, 'duration': '0.5h'},
    ]
}

SCHEDULED_MAINTENANCE = [
    {'date': '2025-01-02', 'equipment': 'Injection Mold Press-A1', 'type': 'Preventive', 'status': 'Scheduled'},
    {'date': '2025-01-05', 'equipment': 'CNC Lathe-B2', 'type': 'Preventive', 'status': 'Scheduled'},
    {'date': '2025-01-08', 'equipment': 'Hydraulic Press-C3', 'type': 'Corrective', 'status': 'Scheduled'},
    {'date': '2025-01-12', 'equipment': 'Assembly Robot-D1', 'type': 'Preventive', 'status': 'Planned'},
    {'date': '2025-01-15', 'equipment': 'Conveyor Belt-E2', 'type': 'Preventive', 'status': 'Scheduled'},
]

# ================== UTILITY FUNCTIONS ==================
def get_health_color(health):
    colors = {
        'Good': '#66BB6A',
        'Fair': '#FFA726',
        'Warning': '#FFA726',
        'Critical': '#EF5350'
    }
    return colors.get(health, '#9E9E9E')

def get_priority_color(priority):
    colors = {
        'Low': '#42A5F5',
        'Medium': '#FFA726',
        'High': '#EF5350',
        'Critical': '#C62828'
    }
    return colors.get(priority, '#9E9E9E')

def get_status_color(status):
    colors = {
        'New': '#0D47A1',
        'In Progress': '#E65100',
        'Repaired': '#1B5E20',
        'Scrap': '#B71C1C'
    }
    return colors.get(status, '#9E9E9E')

def create_metric_card(label, value, subtext="", color="#5C6BC0"):
    """Create a metric card with custom styling"""
    col = st.container()
    with col:
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #E0E0E0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border-top: 3px solid {color};
        ">
            <div style="font-size: 12px; color: #757575; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
                {label}
            </div>
            <div style="font-size: 28px; font-weight: 700; color: #212121; margin: 8px 0;">
                {value}
            </div>
            <div style="font-size: 13px; color: #9E9E9E;">
                {subtext}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================== SIDEBAR NAVIGATION ==================
with st.sidebar:
    st.markdown("### 🔧 GearGuard")
    st.markdown("Enterprise Maintenance Management System")
    st.divider()
    
    # Role selector
    st.markdown("**User Role**")
    role = st.selectbox(
        "Select your role:",
        ["Manager", "Technician", "Employee"],
        label_visibility="collapsed"
    )
    st.session_state.role = role
    
    st.divider()
    st.markdown("**Navigation**")
    
    # Navigation menu
    pages = [
        ("📊 Dashboard", "Dashboard"),
        ("⚙️ Equipment", "Equipment"),
        ("🔧 Maintenance Requests", "Requests"),
        ("📋 Kanban Board", "Kanban"),
        ("📅 Calendar View", "Calendar"),
        ("👨‍🔧 Technician Workspace", "Workspace"),
        ("♻️ Scrap Handling", "Scrap"),
        ("⚙️ Settings", "Settings"),
    ]
    
    for icon_label, page_key in pages:
        if st.button(icon_label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.current_page = page_key
            st.rerun()
    
    st.divider()
    st.markdown("**System Info**")
    st.markdown(f"👤 Role: **{role}**")
    st.markdown(f"🕐 Last sync: **Just now**")

# ================== PAGE: DASHBOARD ==================
def page_dashboard():
    st.markdown(f"<div class='section-header'>📊 Dashboard</div>", unsafe_allow_html=True)
    
    # KPI Cards Row 1
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        create_metric_card("Machines with Most Breakdowns", "3", "Top: CNC Lathe-B2", COLORS['danger'])
    
    with col2:
        create_metric_card("Overdue Tickets", "7", "+2 since yesterday", COLORS['warning'])
    
    with col3:
        create_metric_card("Preventive Tasks Upcoming", "12", "Next 30 days", COLORS['accent'])
    
    with col4:
        create_metric_card("Equipment Health", "4/6", "Good condition", COLORS['primary'])
    
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    # KPI Cards Row 2
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        create_metric_card("Total Downtime (MTH)", "18.5h", "↓ 12% from last month", COLORS['warning'])
    
    with col2:
        create_metric_card("Team Workload", "68%", "7 active technicians", COLORS['secondary'])
    
    with col3:
        create_metric_card("Avg Repair Time", "2.3h", "Within SLA", COLORS['accent'])
    
    st.markdown("<div style='margin: 32px 0;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Charts Section
    st.markdown(f"<div class='subsection-header'>📈 Analytics</div>", unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2, gap="large")
    
    with chart_col1:
        # Breakdown by Equipment Type
        breakdown_data = {
            'Equipment': ['Injection Mold', 'CNC Lathe', 'Hydraulic Press', 'Assembly Robot', 'Conveyor Belt', 'Welding'],
            'Breakdowns': [2, 5, 8, 1, 3, 2]
        }
        fig = px.bar(breakdown_data, x='Equipment', y='Breakdowns', 
                    title='Equipment Breakdowns (Last 30 Days)',
                    color_discrete_sequence=[COLORS['danger']])
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI", size=11),
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        # Request Status Distribution
        status_data = {
            'Status': ['Open', 'In Progress', 'Closed', 'On Hold'],
            'Count': [12, 8, 45, 3]
        }
        fig = px.pie(status_data, names='Status', values='Count',
                    title='Request Status Distribution',
                    color_discrete_sequence=[COLORS['danger'], COLORS['warning'], COLORS['accent'], COLORS['secondary']])
        fig.update_layout(
            paper_bgcolor='white',
            font=dict(family="Segoe UI", size=11),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    # Downtime Trend
    days = pd.date_range(start='2024-12-01', end='2024-12-27', freq='D')
    downtime = np.random.uniform(0.5, 3.5, len(days))
    
    downtime_df = pd.DataFrame({
        'Date': days,
        'Downtime (Hours)': downtime
    })
    
    fig = px.line(downtime_df, x='Date', y='Downtime (Hours)',
                 title='Downtime Trend (Last 30 Days)',
                 markers=True)
    fig.update_traces(line=dict(color=COLORS['primary'], width=3), marker=dict(size=6))
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=11),
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

# ================== PAGE: EQUIPMENT ==================
def page_equipment():
    st.markdown(f"<div class='section-header'>⚙️ Equipment Management</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Equipment List", "📝 Equipment Details"])
    
    with tab1:
        st.markdown(f"<div class='subsection-header'>All Equipment</div>", unsafe_allow_html=True)
        
        # Create a display dataframe with health badges
        display_df = EQUIPMENT_DATA.copy()
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔍 Search equipment...", placeholder="Name or Serial No")
        with col2:
            dept_filter = st.selectbox("Department", ["All"] + EQUIPMENT_DATA['Department'].unique().tolist())
        with col3:
            health_filter = st.selectbox("Health Status", ["All"] + EQUIPMENT_DATA['Health'].unique().tolist())
        
        # Apply filters
        filtered_df = display_df.copy()
        if search:
            filtered_df = filtered_df[
                filtered_df['Name'].str.contains(search, case=False) | 
                filtered_df['Serial No'].str.contains(search, case=False)
            ]
        if dept_filter != "All":
            filtered_df = filtered_df[filtered_df['Department'] == dept_filter]
        if health_filter != "All":
            filtered_df = filtered_df[filtered_df['Health'] == health_filter]
        
        # Display table with custom styling
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        for idx, row in filtered_df.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1.5, 1.5, 1, 1, 1, 1.5], gap="small")
            
            with col1:
                st.markdown(f"**{row['Name']}**")
                st.caption(row['Serial No'])
            
            with col2:
                st.caption(row['Department'])
            
            with col3:
                st.caption(row['Team'])
            
            with col4:
                health_color = get_health_color(row['Health'])
                st.markdown(
                    f'<span style="background: {health_color}22; color: {health_color}; padding: 4px 12px; border-radius: 6px; font-weight: 500; font-size: 12px;">{row["Health"]}</span>',
                    unsafe_allow_html=True
                )
            
            with col5:
                st.caption(row['Warranty'])
            
            with col6:
                st.markdown(f'<span style="background: #E3F2FD; color: #0D47A1; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 11px;">{int(row["Open Requests"])} Open</span>', unsafe_allow_html=True)
            
            with col7:
                if st.button("🔧 Maintenance", key=f"maint_{row['Serial No']}"):
                    st.session_state.selected_equipment = row['Name']
                    st.session_state.current_page = "Requests"
                    st.rerun()
    
    with tab2:
        st.markdown(f"<div class='subsection-header'>Equipment Details & Specifications</div>", unsafe_allow_html=True)
        
        selected_eq = st.selectbox("Select Equipment", EQUIPMENT_DATA['Name'].tolist())
        eq_data = EQUIPMENT_DATA[EQUIPMENT_DATA['Name'] == selected_eq].iloc[0]
        
        # Equipment Details Grid
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("**Basic Information**")
            st.text_input("Equipment Name", value=eq_data['Name'], disabled=True)
            st.text_input("Serial Number", value=eq_data['Serial No'], disabled=True)
            st.text_input("Department", value=eq_data['Department'], disabled=True)
            
        with col2:
            st.markdown("**Assignment & Status**")
            st.text_input("Assigned Team", value=eq_data['Team'], disabled=True)
            st.text_input("Warranty Status", value=eq_data['Warranty'], disabled=True)
            health_color = get_health_color(eq_data['Health'])
            st.markdown(f'<div style="background: white; border-radius: 8px; padding: 12px; border: 1px solid #E0E0E0; margin-top: 8px;">Health Status: <span style="color: {health_color}; font-weight: 700;">{eq_data["Health"]}</span></div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Additional Info
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            st.markdown("**Last Maintenance**")
            st.caption("2024-12-15")
        with col2:
            st.markdown("**Next Due**")
            st.caption("2025-01-15")
        with col3:
            st.markdown("**MTB (Hours)**")
            st.caption("847.5 / 1000")

# ================== PAGE: MAINTENANCE REQUESTS ==================
def page_maintenance_requests():
    st.markdown(f"<div class='section-header'>🔧 Maintenance Requests</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Request List", "➕ Create New Request"])
    
    with tab1:
        st.markdown(f"<div class='subsection-header'>All Requests</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔍 Search requests...", placeholder="Request ID or Equipment")
        with col2:
            status_filter = st.selectbox("Status", ["All"] + MAINTENANCE_REQUESTS['Status'].unique().tolist())
        with col3:
            priority_filter = st.selectbox("Priority", ["All"] + MAINTENANCE_REQUESTS['Priority'].unique().tolist())
        
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        # Apply filters
        filtered_requests = MAINTENANCE_REQUESTS.copy()
        if search:
            filtered_requests = filtered_requests[
                filtered_requests['Request ID'].str.contains(search, case=False) |
                filtered_requests['Equipment'].str.contains(search, case=False)
            ]
        if status_filter != "All":
            filtered_requests = filtered_requests[filtered_requests['Status'] == status_filter]
        if priority_filter != "All":
            filtered_requests = filtered_requests[filtered_requests['Priority'] == priority_filter]
        
        # Display requests as expandable cards
        for idx, req in filtered_requests.iterrows():
            with st.expander(f"**{req['Request ID']}** • {req['Equipment']} • {req['Status']}", expanded=False):
                col1, col2, col3 = st.columns(3, gap="large")
                
                with col1:
                    st.markdown("**Request Details**")
                    st.markdown(f"ID: `{req['Request ID']}`")
                    st.markdown(f"Equipment: **{req['Equipment']}**")
                    st.markdown(f"Category: **{req['Category']}**")
                
                with col2:
                    st.markdown("**Status & Priority**")
                    priority_color = get_priority_color(req['Priority'])
                    st.markdown(f'<span style="background: {priority_color}22; color: {priority_color}; padding: 4px 12px; border-radius: 6px; font-weight: 600; font-size: 12px;">{req["Priority"]}</span>', unsafe_allow_html=True)
                    st.markdown(f"Status: **{req['Status']}**")
                    st.markdown(f"Assigned: **{req['Assigned To']}**")
                
                with col3:
                    st.markdown("**Timeline**")
                    st.markdown(f"Created: **{req['Created Date'].strftime('%Y-%m-%d')}**")
                    st.markdown(f"Days Ago: **{(datetime.now() - req['Created Date']).days} days**")
                
                st.divider()
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👁️ View Details", key=f"view_{req['Request ID']}"):
                        st.session_state.selected_request = req['Request ID']
                        st.session_state.current_page = "Workspace"
                        st.rerun()
                with col2:
                    st.button("✏️ Edit", key=f"edit_{req['Request ID']}")
                with col3:
                    st.button("🗑️ Archive", key=f"archive_{req['Request ID']}")
    
    with tab2:
        st.markdown(f"<div class='subsection-header'>Create New Maintenance Request</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            equipment = st.selectbox("🔧 Select Equipment", EQUIPMENT_DATA['Name'].tolist())
            eq_row = EQUIPMENT_DATA[EQUIPMENT_DATA['Name'] == equipment].iloc[0]
            
            st.text_input("Team (Auto-filled)", value=eq_row['Team'], disabled=True)
            
            category = st.selectbox("Category", ["Preventive Maintenance", "Corrective Maintenance", "Inspection", "Emergency Repair"])
        
        with col2:
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            
            st.text_input("Department (Auto-filled)", value=eq_row['Department'], disabled=True)
            
            assigned_to = st.selectbox("Assign To", ["Auto-assign", "John Doe", "Jane Smith", "Mike Johnson", "Sarah Williams", "Tom Brown"])
        
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        issue_description = st.text_area("📝 Describe the Issue", placeholder="Detailed description of the maintenance issue...", height=120)
        
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✅ Submit Request", use_container_width=True):
                st.success(f"✅ Maintenance Request Created Successfully!\nRequest ID: MR-2025-{np.random.randint(100, 999)}")
        with col2:
            st.button("❌ Clear Form", use_container_width=True)

# ================== PAGE: KANBAN BOARD ==================
def page_kanban():
    st.markdown(f"<div class='section-header'>📋 Kanban Board</div>", unsafe_allow_html=True)
    
    st.markdown("Drag and drop cards to change status. Click to view details.")
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    # Create columns for Kanban
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    columns_data = [
        (col1, "New", "🆕"),
        (col2, "In Progress", "⏳"),
        (col3, "Repaired", "✅"),
        (col4, "Scrap", "♻️")
    ]
    
    for col, status, emoji in columns_data:
        with col:
            st.markdown(f"""
            <div style="
                background: #F5F5F5;
                border-radius: 12px;
                padding: 16px;
                border: 1px solid #E0E0E0;
                min-height: 800px;
            ">
                <div style="
                    font-size: 14px;
                    font-weight: 700;
                    color: #212121;
                    margin-bottom: 16px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    {emoji} {status}
                    <span style="
                        background: white;
                        color: #757575;
                        padding: 2px 8px;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: 600;
                    ">{len(KANBAN_DATA[status])}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Display cards
            for card in KANBAN_DATA[status]:
                overdue_indicator = "🔴 " if card['overdue'] else ""
                priority_color = get_priority_color(card['priority'])
                
                st.markdown(f"""
                <div style="
                    background: white;
                    border-radius: 8px;
                    padding: 14px;
                    margin-bottom: 12px;
                    border: 1px solid #E0E0E0;
                    border-left: 4px solid {priority_color};
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                    cursor: pointer;
                ">
                    <div style="font-size: 12px; color: #757575; margin-bottom: 4px;">{card['id']}</div>
                    <div style="font-size: 13px; font-weight: 600; color: #212121; margin-bottom: 8px;">{card['subject']}</div>
                    <div style="font-size: 11px; color: #9E9E9E; margin-bottom: 10px;">⚙️ {card['equipment']}</div>
                    
                    <div style="display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap;">
                        <span style="background: {priority_color}22; color: {priority_color}; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">
                            {card['priority']}
                        </span>
                        <span style="background: #E3F2FD; color: #0D47A1; padding: 3px 8px; border-radius: 4px; font-size: 10px;">
                            ⏱️ {card['duration']}
                        </span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 8px; border-top: 1px solid #F0F0F0;">
                        <div style="font-size: 10px; color: #757575;">
                            {overdue_indicator}{card['due']}
                        </div>
                        <div style="
                            width: 28px;
                            height: 28px;
                            border-radius: 50%;
                            background: {COLORS['primary']};
                            color: white;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 11px;
                            font-weight: 700;
                        ">
                            {card['tech']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# ================== PAGE: CALENDAR VIEW ==================
def page_calendar():
    st.markdown(f"<div class='section-header'>📅 Calendar View - Preventive Maintenance</div>", unsafe_allow_html=True)
    
    # Month selector
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("◀️ Previous")
    with col2:
        selected_month = st.selectbox("Month", ["January 2025", "December 2024"], index=0)
    with col3:
        st.button("Next ▶️")
    
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    # Calendar grid
    calendar_html = """
    <div style="
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 10px;
        margin-bottom: 24px;
    ">
    """
    
    # Day headers
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for day in days_of_week:
        calendar_html += f'<div style="text-align: center; font-weight: 700; color: #757575; padding: 8px; font-size: 12px;">{day}</div>'
    
    # Calendar dates with events
    events_by_date = {event['date']: event for event in SCHEDULED_MAINTENANCE}
    
    # January 2025 starts on Wednesday
    for empty in range(3):
        calendar_html += '<div></div>'
    
    for day in range(1, 32):
        date_str = f"2025-01-{day:02d}"
        has_event = date_str in events_by_date
        event = events_by_date.get(date_str)
        
        bg_color = "#E8F5E9" if has_event else "white"
        border_color = "#66BB6A" if has_event else "#E0E0E0"
        
        calendar_html += f"""
        <div style="
            background: {bg_color};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 12px;
            min-height: 100px;
            cursor: pointer;
            transition: all 0.2s;
        ">
            <div style="font-weight: 700; color: #212121; margin-bottom: 8px;">{day}</div>
        """
        
        if has_event:
            color_map = {"Preventive": "#66BB6A", "Corrective": "#EF5350"}
            event_color = color_map.get(event['type'], "#42A5F5")
            calendar_html += f"""
            <div style="
                background: {event_color};
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: 600;
                margin-bottom: 4px;
            ">
                {event['type']}
            </div>
            <div style="font-size: 9px; color: #424242; line-height: 1.3;">
                {event['equipment']}
            </div>
            """
        
        calendar_html += "</div>"
    
    calendar_html += "</div>"
    
    st.markdown(calendar_html, unsafe_allow_html=True)
    
    st.divider()
    
    # Upcoming scheduled maintenance list
    st.markdown(f"<div class='subsection-header'>📋 Upcoming Scheduled Maintenance</div>", unsafe_allow_html=True)
    
    for event in SCHEDULED_MAINTENANCE:
        color_map = {"Preventive": "#66BB6A", "Corrective": "#EF5350"}
        event_color = color_map.get(event['type'], "#42A5F5")
        
        col1, col2, col3, col4 = st.columns([1.5, 2, 1.5, 1], gap="medium")
        
        with col1:
            st.markdown(f"**{event['date']}**")
        
        with col2:
            st.caption(event['equipment'])
        
        with col3:
            st.markdown(f'<span style="background: {event_color}22; color: {event_color}; padding: 4px 12px; border-radius: 6px; font-weight: 600; font-size: 12px;">{event["type"]}</span>', unsafe_allow_html=True)
        
        with col4:
            status_color = "#66BB6A" if event['status'] == 'Scheduled' else "#FFA726"
            st.markdown(f'<span style="background: {status_color}22; color: {status_color}; padding: 4px 8px; border-radius: 4px; font-size: 11px;">{event["status"]}</span>', unsafe_allow_html=True)

# ================== PAGE: TECHNICIAN WORKSPACE ==================
def page_technician_workspace():
    st.markdown(f"<div class='section-header'>👨‍🔧 Technician Workspace</div>", unsafe_allow_html=True)
    
    # Task assignment UI
    st.markdown(f"<div class='subsection-header'>Assigned Tasks</div>", unsafe_allow_html=True)
    
    tasks = [
        {'id': 'K-003', 'equipment': 'Hydraulic Press-C3', 'issue': 'Hydraulic seal replacement', 'priority': 'Critical', 'status': 'In Progress'},
        {'id': 'K-004', 'equipment': 'Injection Mold Press-A1', 'issue': 'Calibration check', 'priority': 'Low', 'status': 'Not Started'},
    ]
    
    for task in tasks:
        col1, col2, col3 = st.columns([3, 1, 0.8], gap="small")
        
        with col1:
            with st.expander(f"**{task['id']}** • {task['equipment']} • {task['status']}", expanded=(task['status'] == 'In Progress')):
                
                col_a, col_b = st.columns(2, gap="large")
                
                with col_a:
                    st.markdown("**Task Details**")
                    st.markdown(f"ID: `{task['id']}`")
                    st.markdown(f"Equipment: **{task['equipment']}**")
                    st.markdown(f"Issue: **{task['issue']}**")
                
                with col_b:
                    st.markdown("**Status**")
                    priority_color = get_priority_color(task['priority'])
                    st.markdown(f'<span style="background: {priority_color}22; color: {priority_color}; padding: 4px 12px; border-radius: 6px; font-weight: 600; font-size: 12px;">{task["priority"]}</span>', unsafe_allow_html=True)
                    st.markdown(f"Current: **{task['Status']}**")
                
                st.divider()
                
                # Timer and notes section
                st.markdown("**Work Progress**")
                
                col_t1, col_t2 = st.columns([2, 1], gap="medium")
                
                with col_t1:
                    if not st.session_state.task_running:
                        if st.button("▶️ Start Task", use_container_width=True):
                            st.session_state.task_running = True
                            st.rerun()
                    else:
                        st.markdown(f"<div style='background: #FFF3E0; border-radius: 8px; padding: 16px; text-align: center;'><div style='font-size: 24px; font-weight: 700; color: #F57F17; margin-bottom: 8px;'>⏱️ 02:15</div><div style='font-size: 12px; color: #666;'>Task in progress...</div></div>", unsafe_allow_html=True)
                        
                        col_stop1, col_stop2 = st.columns(2, gap="small")
                        with col_stop1:
                            if st.button("⏸️ Pause", use_container_width=True):
                                st.session_state.task_running = False
                        with col_stop2:
                            if st.button("⏹️ Stop", use_container_width=True):
                                st.session_state.task_running = False
                
                with col_t2:
                    st.markdown("**Time Spent**")
                    st.caption("02:15 hours")
                
                st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
                
                # Notes section
                st.markdown("**Work Notes**")
                notes = st.text_area("Add notes about the work...", placeholder="Document your findings and actions taken", height=100, key=f"notes_{task['id']}")
                
                st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
                
                # Upload images
                st.markdown("**Attachments**")
                uploaded_files = st.file_uploader("Upload photos of the work", accept_multiple_files=True, key=f"upload_{task['id']}")
                if uploaded_files:
                    st.success(f"✅ {len(uploaded_files)} file(s) ready to upload")
                
                st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
                
                # Status change
                col_status1, col_status2 = st.columns(2, gap="medium")
                
                with col_status1:
                    new_status = st.selectbox("Change Status", ["In Progress", "Completed", "On Hold", "Needs Approval"], key=f"status_{task['id']}")
                
                with col_status2:
                    if st.button("💾 Save Changes", use_container_width=True):
                        st.success("✅ Changes saved!")
        
        with col2:
            st.markdown("")
        
        with col3:
            st.markdown("")

# ================== PAGE: SCRAP HANDLING ==================
def page_scrap_handling():
    st.markdown(f"<div class='section-header'>♻️ Scrap Handling</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='subsection-header'>Equipment Scrap Management</div>", unsafe_allow_html=True)
    
    # Scrap items list
    scrap_items = [
        {'equipment': 'CNC Lathe-B2 Bearing Assembly', 'reason': 'Defective bearing', 'date': '2024-12-20', 'status': 'Pending Approval'},
        {'equipment': 'Conveyor Belt-E2 Drive Unit', 'reason': 'Beyond repair', 'date': '2024-12-18', 'status': 'Approved'},
    ]
    
    for item in scrap_items:
        status_color = "#FFA726" if item['status'] == 'Pending Approval' else "#66BB6A"
        
        with st.expander(f"**{item['equipment']}** • {item['status']}", expanded=False):
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown("**Item Details**")
                st.text_input("Equipment/Part", value=item['equipment'], disabled=True)
                st.text_input("Reason for Scrapping", value=item['reason'], disabled=True)
                st.text_input("Date Flagged", value=item['date'], disabled=True)
            
            with col2:
                st.markdown("**Approval Status**")
                st.markdown(f'<div style="background: {status_color}22; border-radius: 8px; padding: 16px; text-align: center;"><div style="color: {status_color}; font-weight: 700; font-size: 14px;">{item["status"]}</div></div>', unsafe_allow_html=True)
                
                st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
                
                approval_notes = st.text_area("Approval Notes", placeholder="Add notes for scrap approval...", height=80, key=f"scrap_notes_{item['equipment']}")
            
            st.divider()
            
            # Action buttons
            if item['status'] == 'Pending Approval':
                col_a1, col_a2, col_a3 = st.columns(3, gap="medium")
                with col_a1:
                    if st.button("✅ Approve", use_container_width=True, key=f"approve_{item['equipment']}"):
                        st.success("✅ Scrap item approved!")
                with col_a2:
                    if st.button("❌ Reject", use_container_width=True, key=f"reject_{item['equipment']}"):
                        st.error("❌ Scrap item rejected!")
                with col_a3:
                    if st.button("⏸️ Hold", use_container_width=True, key=f"hold_{item['equipment']}"):
                        st.info("⏸️ Item marked on hold!")
            else:
                col_a1, col_a2 = st.columns(2, gap="medium")
                with col_a1:
                    if st.button("🗑️ Remove from System", use_container_width=True, key=f"remove_{item['equipment']}"):
                        st.success("✅ Item removed from active equipment!")
                with col_a2:
                    if st.button("📄 Generate Certificate", use_container_width=True, key=f"cert_{item['equipment']}"):
                        st.info("📄 Scrap certificate generated!")
    
    st.divider()
    
    st.markdown(f"<div class='subsection-header'>Flag New Equipment for Scrap</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        equipment_to_scrap = st.selectbox("Select Equipment", EQUIPMENT_DATA['Name'].tolist())
        scrap_reason = st.selectbox("Reason", ["Beyond Repair", "Defective Component", "End of Life", "Safety Hazard", "Other"])
    
    with col2:
        scrap_notes = st.text_area("Additional Notes", placeholder="Explain why this equipment should be scrapped...", height=120)
    
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    col_submit, col_cancel = st.columns(2, gap="medium")
    with col_submit:
        if st.button("🚩 Flag for Scrap", use_container_width=True):
            st.warning(f"⚠️ '{equipment_to_scrap}' has been flagged for scrap approval.\nAwaiting manager review...")
    with col_cancel:
        st.button("Clear Form", use_container_width=True)

# ================== PAGE: SETTINGS ==================
def page_settings():
    st.markdown(f"<div class='section-header'>⚙️ Settings</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 User Settings", "🔔 Notifications", "🔐 Security"])
    
    with tab1:
        st.markdown(f"<div class='subsection-header'>User Profile</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.text_input("Full Name", value="John Doe")
            st.text_input("Email", value="john.doe@gearguard.com")
            st.text_input("Department", value="Manufacturing")
            st.text_input("Role", value=st.session_state.role, disabled=True)
        
        with col2:
            st.text_input("Phone", value="+1-555-0123")
            st.text_input("Employee ID", value="EMP-2021-001", disabled=True)
            st.text_input("Team", value="Team A")
            st.text_input("Joined", value="2021-03-15", disabled=True)
        
        st.divider()
        st.button("💾 Save Changes", use_container_width=True)
    
    with tab2:
        st.markdown(f"<div class='subsection-header'>Notification Preferences</div>", unsafe_allow_html=True)
        
        st.toggle("🔔 Equipment Alerts", value=True, help="Notify when equipment status changes")
        st.toggle("⏰ Due Maintenance Reminders", value=True, help="Remind about upcoming maintenance")
        st.toggle("📧 Email Notifications", value=True, help="Send notifications via email")
        st.toggle("📱 SMS Alerts", value=False, help="Send urgent alerts via SMS")
        st.toggle("🔊 Sound Alerts", value=True, help="Play sound for critical alerts")
    
    with tab3:
        st.markdown(f"<div class='subsection-header'>Security & Access</div>", unsafe_allow_html=True)
        
        st.markdown("**Password**")
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.text_input("Current Password", type="password", value="••••••••", disabled=True)
        with col2:
            st.button("🔑 Change Password", use_container_width=True)
        
        st.divider()
        
        st.markdown("**Two-Factor Authentication**")
        st.toggle("Enable 2FA", value=False, help="Add extra security with two-factor authentication")

# ================== MAIN APP ROUTER ==================
def main():
    page = st.session_state.current_page
    
    if page == "Dashboard":
        page_dashboard()
    elif page == "Equipment":
        page_equipment()
    elif page == "Requests":
        page_maintenance_requests()
    elif page == "Kanban":
        page_kanban()
    elif page == "Calendar":
        page_calendar()
    elif page == "Workspace":
        page_technician_workspace()
    elif page == "Scrap":
        page_scrap_handling()
    elif page == "Settings":
        page_settings()
    else:
        page_dashboard()

if __name__ == "__main__":
    main()
