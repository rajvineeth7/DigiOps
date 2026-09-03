


import streamlit as st
import sqlite3
from datetime import date, datetime
import calendar
import html


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DigiOps",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# DATABASE
# ============================================================

DB_FILE = "digi_ops.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # Calendar / Daily Notes
    # Each employee has separate notes for each date.
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            note_date TEXT NOT NULL,
            task TEXT DEFAULT '',
            completed TEXT DEFAULT '',
            important TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(username, note_date)
        )
    """)

    # --------------------------------------------------------
    # Projects
    # Each project belongs to one employee.
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            project_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Started',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # Workflow steps
    # Each project gets its own 30 workflow steps.
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflow_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            step_name TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            UNIQUE(project_id, step_number),
            FOREIGN KEY(project_id)
                REFERENCES projects(id)
                ON DELETE CASCADE
        )
    """)

    # --------------------------------------------------------
    # Activities
    # Each activity belongs to one employee.
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            activity_date TEXT NOT NULL,
            activity TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


initialize_database()


# ============================================================
# LOGIN USERS
# ============================================================

USERS = {
    "Farid": {
        "password": "farid123",
        "role": "user"
    },

    "Suseendra": {
        "password": "suseendra123",
        "role": "user"
    },

    "Srihari": {
        "password": "srihari123",
        "role": "user"
    },

    "Rajvineeth": {
        "password": "raj123",
        "role": "user"
    },

    "Manager": {
        "password": "12345678",
        "role": "admin"
    }
}


# ============================================================
# PROJECT STATUS
# ============================================================

PROJECT_STATUSES = {
    "Started": "#ffffff",
    "Running": "#f2c94c",
    "Hold": "#e74c3c",
    "Completed": "#27ae60",
    "Maintenance": "#3498db",
    "Terminated": "#000000"
}


# ============================================================
# 30 PROJECT WORKFLOW STEPS
# ============================================================

WORKFLOW_STEPS = [
    "URS DOC",
    "URS DOC SIGNOFF",
    "REQUEST FOR PROPOSAL & NON DISCLOSURE AGREEMENT",
    "VENDOR DEMO",
    "FUNCTIONAL EVALUATION",
    "TECHNICAL EVALUATION",
    "COMMERCIAL EVALUATION",
    "VENDOR FINALIZATION",
    "PROJECT CHARTER PREPARE",
    "PROJECT CHARTER SIGNOFF",
    "COMMERCIAL NEGOTIATION SIGNOFF",
    "NOTE FOR APPROVAL",
    "NFA SIGNOFF",
    "PURCHASE REQUISITION",
    "PURCHASE ORDER",
    "AS-IS",
    "TO-BE",
    "TECHNICAL DESIGN FINALIZED",
    "PRODUCT DEVELOPING",
    "PRODUCT CONFIGURATION",
    "UNIT TESTING",
    "IQ & SIGNOFF",
    "USER ACCEPTANCE TESTING",
    "UAT AMENDMENTS",
    "OQ & SIGNOFF",
    "PQ & READY TO DEPLOY",
    "GO LIVE",
    "BUSINESS ADOPTION",
    "KPI MONITORING",
    "PRODUCT LIFECYCLE MANAGEMENT"
]


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #f7faff;
}

/* Main headings */

.main-title {
    font-size: 38px;
    font-weight: 700;
    color: #1261a0;
    margin-bottom: 4px;
}

.page-title {
    font-size: 28px;
    font-weight: 700;
    color: #1261a0;
    margin-bottom: 18px;
}

.subtitle {
    color: #657786;
    font-size: 15px;
}

/* Cards */

.card {
    background: #ffffff;
    border: 1px solid #dce6ef;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 12px;
}

.card-title {
    color: #1261a0;
    font-size: 19px;
    font-weight: 650;
}

/* Project */

.project-card {
    background: #ffffff;
    border: 1px solid #dce6ef;
    border-radius: 9px;
    padding: 14px 18px;
    margin-bottom: 8px;
}

/* Status dot */

.status-dot {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 7px;
    border: 1px solid #999999;
    vertical-align: middle;
}

/* Workflow */

.workflow-row {
    background: #ffffff;
    border: 1px solid #dce6ef;
    border-radius: 8px;
    padding: 13px 15px;
    margin-bottom: 7px;
}

.workflow-name {
    color: #273746;
    font-size: 15px;
}

/* Metrics */

.metric-box {
    background: #ffffff;
    border: 1px solid #dce6ef;
    border-radius: 10px;
    padding: 18px;
    text-align: center;
}

.metric-number {
    color: #1261a0;
    font-size: 28px;
    font-weight: 700;
}

.metric-label {
    color: #667786;
    font-size: 13px;
}

/* Login */

.login-box {
    background: #ffffff;
    border: 1px solid #dce6ef;
    border-radius: 12px;
    padding: 25px;
}

/* Buttons */

div.stButton > button {
    border-radius: 7px;
    border: 1px solid #cbd9e5;
}

div.stButton > button:hover {
    border-color: #1261a0;
    color: #1261a0;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def now_string():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_text(value):
    return html.escape(str(value or ""))


def status_dot(status):

    color = PROJECT_STATUSES.get(status, "#999999")

    border = "1px solid #999999"

    if status == "Terminated":
        border = "1px solid #333333"

    return (
        f'<span class="status-dot" '
        f'style="background-color:{color};'
        f'border:{border};"></span>'
    )


def workflow_dot(completed):

    color = "#27ae60" if completed else "#e74c3c"

    return (
        f'<span class="status-dot" '
        f'style="background-color:{color};'
        f'border:1px solid #999;"></span>'
    )


def render_bullet_text(text):

    if not text or not text.strip():
        st.caption("No entries.")
        return

    for line in text.splitlines():

        line = line.strip()

        if line:

            st.markdown(
                f"- {safe_text(line)}"
            )


# ============================================================
# DAILY NOTES
# ============================================================

def get_daily_note(username, note_date):

    conn = get_connection()

    row = conn.execute("""
        SELECT *
        FROM daily_notes
        WHERE username = ?
        AND note_date = ?
    """, (
        username,
        note_date
    )).fetchone()

    conn.close()

    return row


def save_daily_note(
    username,
    note_date,
    task,
    completed,
    important
):

    conn = get_connection()

    timestamp = now_string()

    existing = conn.execute("""
        SELECT id
        FROM daily_notes
        WHERE username = ?
        AND note_date = ?
    """, (
        username,
        note_date
    )).fetchone()

    if existing:

        conn.execute("""
            UPDATE daily_notes
            SET task = ?,
                completed = ?,
                important = ?,
                updated_at = ?
            WHERE username = ?
            AND note_date = ?
        """, (
            task,
            completed,
            important,
            timestamp,
            username,
            note_date
        ))

    else:

        conn.execute("""
            INSERT INTO daily_notes
            (
                username,
                note_date,
                task,
                completed,
                important,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            note_date,
            task,
            completed,
            important,
            timestamp,
            timestamp
        ))

    conn.commit()
    conn.close()


def get_important_dates(
    username,
    year,
    month
):

    conn = get_connection()

    prefix = f"{year:04d}-{month:02d}"

    rows = conn.execute("""
        SELECT note_date
        FROM daily_notes
        WHERE username = ?
        AND note_date LIKE ?
        AND TRIM(important) != ''
    """, (
        username,
        prefix + "%"
    )).fetchall()

    conn.close()

    return {
        row["note_date"]
        for row in rows
    }


# ============================================================
# PROJECTS
# ============================================================

def get_projects(username=None):

    conn = get_connection()

    if username:

        rows = conn.execute("""
            SELECT *
            FROM projects
            WHERE username = ?
            ORDER BY id DESC
        """, (
            username,
        )).fetchall()

    else:

        rows = conn.execute("""
            SELECT *
            FROM projects
            ORDER BY username, id DESC
        """).fetchall()

    conn.close()

    return rows


def get_project(project_id):

    conn = get_connection()

    row = conn.execute("""
        SELECT *
        FROM projects
        WHERE id = ?
    """, (
        project_id,
    )).fetchone()

    conn.close()

    return row


def create_project(
    username,
    project_name,
    status
):

    conn = get_connection()

    cursor = conn.cursor()

    timestamp = now_string()

    cursor.execute("""
        INSERT INTO projects
        (
            username,
            project_name,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        project_name,
        status,
        timestamp,
        timestamp
    ))

    project_id = cursor.lastrowid

    # Create all 30 workflow steps
    for number, step_name in enumerate(
        WORKFLOW_STEPS,
        start=1
    ):

        cursor.execute("""
            INSERT INTO workflow_steps
            (
                project_id,
                step_number,
                step_name,
                completed
            )
            VALUES (?, ?, ?, 0)
        """, (
            project_id,
            number,
            step_name
        ))

    conn.commit()
    conn.close()


def update_project(
    project_id,
    project_name,
    status
):

    conn = get_connection()

    conn.execute("""
        UPDATE projects
        SET project_name = ?,
            status = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        project_name,
        status,
        now_string(),
        project_id
    ))

    conn.commit()
    conn.close()


def delete_project(project_id):

    conn = get_connection()

    conn.execute("""
        DELETE FROM workflow_steps
        WHERE project_id = ?
    """, (
        project_id,
    ))

    conn.execute("""
        DELETE FROM projects
        WHERE id = ?
    """, (
        project_id,
    ))

    conn.commit()
    conn.close()


# ============================================================
# WORKFLOW
# ============================================================

def get_workflow(project_id):

    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM workflow_steps
        WHERE project_id = ?
        ORDER BY step_number
    """, (
        project_id,
    )).fetchall()

    conn.close()

    return rows


def set_workflow_status(
    project_id,
    step_number,
    completed
):

    conn = get_connection()

    conn.execute("""
        UPDATE workflow_steps
        SET completed = ?
        WHERE project_id = ?
        AND step_number = ?
    """, (
        1 if completed else 0,
        project_id,
        step_number
    ))

    conn.commit()
    conn.close()


# ============================================================
# ACTIVITIES
# ============================================================

def get_activities(username):

    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM activities
        WHERE username = ?
        ORDER BY activity_date DESC, id DESC
    """, (
        username,
    )).fetchall()

    conn.close()

    return rows


def add_activity(
    username,
    activity_date,
    activity
):

    conn = get_connection()

    conn.execute("""
        INSERT INTO activities
        (
            username,
            activity_date,
            activity,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        username,
        activity_date,
        activity,
        now_string()
    ))

    conn.commit()
    conn.close()


def delete_activity(activity_id):

    conn = get_connection()

    conn.execute("""
        DELETE FROM activities
        WHERE id = ?
    """, (
        activity_id,
    ))

    conn.commit()
    conn.close()


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

if "calendar_year" not in st.session_state:
    st.session_state.calendar_year = date.today().year

if "calendar_month" not in st.session_state:
    st.session_state.calendar_month = date.today().month

if "admin_selected_project" not in st.session_state:
    st.session_state.admin_selected_project = None


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    st.markdown(
        '<div class="main-title">DigiOps</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Digital Operations Project Management'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")
    st.divider()
    st.write("")

    left, center, right = st.columns([1, 2, 1])

    with center:

        st.markdown(
            '<div class="login-box">',
            unsafe_allow_html=True
        )

        st.subheader("Login")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        login = st.button(
            "Login",
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        if login:

            if username in USERS:

                if password == USERS[username]["password"]:

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = USERS[username]["role"]

                    if USERS[username]["role"] == "admin":

                        st.session_state.page = "admin"

                    else:

                        st.session_state.page = "home"

                    st.rerun()

                else:

                    st.error(
                        "Incorrect password."
                    )

            else:

                st.error(
                    "Username not found."
                )


# ============================================================
# USER HEADER / NAVIGATION
# ============================================================

def user_navigation():

    username = st.session_state.username

    st.markdown(
        '<div class="main-title">DigiOps</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="subtitle">'
        f'Welcome, {safe_text(username)}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        if st.button(
            "Home",
            use_container_width=True
        ):

            st.session_state.page = "home"
            st.session_state.selected_project = None
            st.session_state.selected_date = None

            st.rerun()

    with col2:

        if st.button(
            "Calendar",
            use_container_width=True
        ):

            st.session_state.page = "calendar"
            st.session_state.selected_date = None

            st.rerun()

    with col3:

        if st.button(
            "Projects",
            use_container_width=True
        ):

            st.session_state.page = "projects"
            st.session_state.selected_project = None

            st.rerun()

    with col4:

        if st.button(
            "Activities",
            use_container_width=True
        ):

            st.session_state.page = "activities"

            st.rerun()

    st.divider()


# ============================================================
# USER HOME
# ============================================================

def user_home():

    username = st.session_state.username

    st.markdown(
        '<div class="page-title">My DigiOps</div>',
        unsafe_allow_html=True
    )

    st.write(
        f"Your personal workspace for "
        f"Calendar, Projects and Activities."
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""
        <div class="card">
            <div class="card-title">
                Calendar
            </div>
            <br>
            Manage daily tasks, completed work
            and important notes.
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Open Calendar",
            use_container_width=True
        ):

            st.session_state.page = "calendar"
            st.rerun()

    with col2:

        st.markdown("""
        <div class="card">
            <div class="card-title">
                Projects
            </div>
            <br>
            Manage your projects and track
            every workflow stage.
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Open Projects",
            use_container_width=True
        ):

            st.session_state.page = "projects"
            st.rerun()

    with col3:

        st.markdown("""
        <div class="card">
            <div class="card-title">
                Activities
            </div>
            <br>
            Store additional daily operational
            information and important activities.
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Open Activities",
            use_container_width=True
        ):

            st.session_state.page = "activities"
            st.rerun()


# ============================================================
# CALENDAR PAGE
# ============================================================

def calendar_page():

    username = st.session_state.username

    st.markdown(
        '<div class="page-title">My Calendar</div>',
        unsafe_allow_html=True
    )

    year = st.session_state.calendar_year
    month = st.session_state.calendar_month

    important_dates = get_important_dates(
        username,
        year,
        month
    )

    previous_col, title_col, next_col = st.columns(
        [1, 4, 1]
    )

    with previous_col:

        if st.button(
            "Previous",
            use_container_width=True
        ):

            month -= 1

            if month == 0:
                month = 12
                year -= 1

            st.session_state.calendar_year = year
            st.session_state.calendar_month = month

            st.rerun()

    with title_col:

        st.markdown(
            f"""
            <h2 style="
                text-align:center;
                color:#1261a0;
                margin-top:0;
            ">
                {calendar.month_name[month]} {year}
            </h2>
            """,
            unsafe_allow_html=True
        )

    with next_col:

        if st.button(
            "Next",
            use_container_width=True
        ):

            month += 1

            if month == 13:
                month = 1
                year += 1

            st.session_state.calendar_year = year
            st.session_state.calendar_month = month

            st.rerun()

    st.write("")

    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    cols = st.columns(7)

    for index, weekday in enumerate(weekdays):

        with cols[index]:

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-weight:700;
                    color:#1261a0;
                    margin-bottom:8px;
                ">
                    {weekday[:3]}
                </div>
                """,
                unsafe_allow_html=True
            )

    month_calendar = calendar.monthcalendar(
        year,
        month
    )

    for week in month_calendar:

        cols = st.columns(7)

        for index, day_number in enumerate(week):

            with cols[index]:

                if day_number == 0:

                    st.write("")

                else:

                    current_date = date(
                        year,
                        month,
                        day_number
                    )

                    date_string = current_date.isoformat()

                    star = ""

                    if date_string in important_dates:
                        star = " ★"

                    if st.button(
                        f"{day_number}{star}",
                        key=f"date_{date_string}",
                        use_container_width=True
                    ):

                        st.session_state.selected_date = date_string

                        st.rerun()

    st.divider()

    if st.session_state.selected_date:

        daily_note_page(
            st.session_state.selected_date
        )


# ============================================================
# DAILY NOTE PAGE
# ============================================================

def daily_note_page(selected_date):

    username = st.session_state.username

    row = get_daily_note(
        username,
        selected_date
    )

    task_value = row["task"] if row else ""
    completed_value = row["completed"] if row else ""
    important_value = row["important"] if row else ""

    selected_date_obj = datetime.strptime(
        selected_date,
        "%Y-%m-%d"
    ).date()

    st.markdown(
        f"### {selected_date_obj.strftime('%d %B %Y')}"
    )

    edit_key = f"editing_{username}_{selected_date}"

    if not st.session_state.get(
        edit_key,
        False
    ):

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("#### Task")

            render_bullet_text(
                task_value
            )

        with col2:

            st.markdown("#### Completed")

            render_bullet_text(
                completed_value
            )

        with col3:

            st.markdown("#### Important")

            if important_value.strip():

                st.markdown(
                    "★ Important",
                    unsafe_allow_html=True
                )

            render_bullet_text(
                important_value
            )

        st.write("")

        edit_col, back_col = st.columns(2)

        with edit_col:

            if st.button(
                "Edit",
                use_container_width=True
            ):

                st.session_state[
                    edit_key
                ] = True

                st.rerun()

        with back_col:

            if st.button(
                "Back",
                use_container_width=True
            ):

                st.session_state.selected_date = None

                st.rerun()

    else:

        task = st.text_area(
            "Task",
            value=task_value,
            height=140,
            placeholder="Enter tasks. One point per line."
        )

        completed = st.text_area(
            "Completed",
            value=completed_value,
            height=140,
            placeholder="Enter completed items. One point per line."
        )

        important = st.text_area(
            "Important",
            value=important_value,
            height=140,
            placeholder="Enter important items. One point per line."
        )

        save_col, back_col = st.columns(2)

        with save_col:

            if st.button(
                "Save",
                use_container_width=True
            ):

                save_daily_note(
                    username,
                    selected_date,
                    task,
                    completed,
                    important
                )

                st.session_state[
                    edit_key
                ] = False

                st.rerun()

        with back_col:

            if st.button(
                "Back",
                use_container_width=True
            ):

                st.session_state[
                    edit_key
                ] = False

                st.rerun()


# ============================================================
# PROJECTS PAGE
# ============================================================

def projects_page():

    username = st.session_state.username

    st.markdown(
        '<div class="page-title">My Projects</div>',
        unsafe_allow_html=True
    )

    st.write(
        f"Projects owned by {username}."
    )

    st.write("")

    if st.button(
        "Add Project",
        use_container_width=True
    ):

        st.session_state.adding_project = True

    if st.session_state.get(
        "adding_project",
        False
    ):

        st.divider()

        st.subheader("Add New Project")

        project_name = st.text_input(
            "Project Name",
            key="new_project_name"
        )

        status = st.selectbox(
            "Project Status",
            list(PROJECT_STATUSES.keys()),
            key="new_project_status"
        )

        save_col, cancel_col = st.columns(2)

        with save_col:

            if st.button(
                "Save Project",
                use_container_width=True
            ):

                if project_name.strip():

                    create_project(
                        username,
                        project_name.strip(),
                        status
                    )

                    st.session_state.adding_project = False

                    st.rerun()

                else:

                    st.warning(
                        "Please enter a project name."
                    )

        with cancel_col:

            if st.button(
                "Cancel",
                use_container_width=True
            ):

                st.session_state.adding_project = False

                st.rerun()

    st.divider()

    projects = get_projects(username)

    if not projects:

        st.info(
            "You have not created any projects yet."
        )

        return

    for project in projects:

        project_id = project["id"]
        project_name = project["project_name"]
        current_status = project["status"]

        st.markdown(
            f"""
            <div class="project-card">
                <strong>
                    {safe_text(project_name)}
                </strong>
                &nbsp;&nbsp;
                {status_dot(current_status)}
                <span>
                    {safe_text(current_status)}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        open_col, menu_col = st.columns(
            [8, 1]
        )

        with open_col:

            if st.button(
                f"Open {project_name}",
                key=f"open_{project_id}",
                use_container_width=True
            ):

                st.session_state.selected_project = project_id

                st.rerun()

        with menu_col:

            with st.popover("⋮"):

                st.write("Project Options")

                status_choice = st.selectbox(
                    "Status",
                    list(PROJECT_STATUSES.keys()),
                    index=list(
                        PROJECT_STATUSES.keys()
                    ).index(current_status),
                    key=f"status_select_{project_id}"
                )

                if st.button(
                    "Update Status",
                    key=f"status_update_{project_id}",
                    use_container_width=True
                ):

                    update_project(
                        project_id,
                        project_name,
                        status_choice
                    )

                    st.rerun()

                if st.button(
                    "Edit Project",
                    key=f"edit_{project_id}",
                    use_container_width=True
                ):

                    st.session_state[
                        f"editing_{project_id}"
                    ] = True

                    st.rerun()

                if st.button(
                    "Delete Project",
                    key=f"delete_{project_id}",
                    use_container_width=True
                ):

                    delete_project(
                        project_id
                    )

                    st.session_state.selected_project = None

                    st.rerun()

        # ----------------------------------------------------
        # EDIT PROJECT
        # ----------------------------------------------------

        if st.session_state.get(
            f"editing_{project_id}",
            False
        ):

            edited_name = st.text_input(
                "Project Name",
                value=project_name,
                key=f"edited_name_{project_id}"
            )

            edited_status = st.selectbox(
                "Status",
                list(PROJECT_STATUSES.keys()),
                index=list(
                    PROJECT_STATUSES.keys()
                ).index(current_status),
                key=f"edited_status_{project_id}"
            )

            save_col, cancel_col = st.columns(2)

            with save_col:

                if st.button(
                    "Save Changes",
                    key=f"save_changes_{project_id}",
                    use_container_width=True
                ):

                    update_project(
                        project_id,
                        edited_name.strip(),
                        edited_status
                    )

                    st.session_state[
                        f"editing_{project_id}"
                    ] = False

                    st.rerun()

            with cancel_col:

                if st.button(
                    "Cancel",
                    key=f"cancel_changes_{project_id}",
                    use_container_width=True
                ):

                    st.session_state[
                        f"editing_{project_id}"
                    ] = False

                    st.rerun()


# ============================================================
# PROJECT WORKFLOW
# ============================================================

def project_workflow_page(project_id):

    username = st.session_state.username

    project = get_project(project_id)

    # Security check:
    # Employee can only open their own project.
    if not project or project["username"] != username:

        st.error(
            "You do not have access to this project."
        )

        if st.button("Back"):

            st.session_state.selected_project = None

            st.rerun()

        return

    st.markdown(
        f'<div class="page-title">'
        f'{safe_text(project["project_name"])}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="card">
            <strong>Owner:</strong>
            {safe_text(project["username"])}
            &nbsp;&nbsp;&nbsp;&nbsp;
            <strong>Status:</strong>
            {status_dot(project["status"])}
            {safe_text(project["status"])}
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Back to Projects"
    ):

        st.session_state.selected_project = None

        st.rerun()

    st.divider()

    workflow = get_workflow(
        project_id
    )

    completed_count = sum(
        1
        for step in workflow
        if step["completed"]
    )

    total_steps = len(workflow)

    progress = (
        completed_count / total_steps
        if total_steps
        else 0
    )

    st.progress(
        progress
    )

    st.write(
        f"Workflow Progress: "
        f"**{completed_count} / {total_steps} completed**"
    )

    st.write("")

    for step in workflow:

        step_number = step["step_number"]
        step_name = step["step_name"]
        completed = bool(step["completed"])

        left, right = st.columns(
            [9, 1]
        )

        with left:

            st.markdown(
                f"""
                <div class="workflow-row">
                    {workflow_dot(completed)}
                    <span class="workflow-name">
                        <strong>{step_number}.</strong>
                        {safe_text(step_name)}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with right:

            with st.popover("⋮"):

                current_status = (
                    "Completed"
                    if completed
                    else "Not Completed"
                )

                selected_status = st.radio(
                    "Step Status",
                    [
                        "Completed",
                        "Not Completed"
                    ],
                    index=(
                        0
                        if completed
                        else 1
                    ),
                    key=f"step_{project_id}_{step_number}"
                )

                if selected_status != current_status:

                    set_workflow_status(
                        project_id,
                        step_number,
                        selected_status == "Completed"
                    )

                    st.rerun()


# ============================================================
# ACTIVITIES PAGE
# ============================================================

def activities_page():

    username = st.session_state.username

    st.markdown(
        '<div class="page-title">My Activities</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Store additional daily information, "
        "observations or important activities."
    )

    st.divider()

    activity_date = st.date_input(
        "Date",
        value=date.today()
    )

    activity = st.text_area(
        "Activity / Information",
        height=150,
        placeholder="Enter activity or important information..."
    )

    if st.button(
        "Save Activity",
        use_container_width=True
    ):

        if activity.strip():

            add_activity(
                username,
                activity_date.isoformat(),
                activity.strip()
            )

            st.success(
                "Activity saved."
            )

            st.rerun()

        else:

            st.warning(
                "Please enter activity information."
            )

    st.divider()

    st.subheader(
        "My Activity History"
    )

    activities = get_activities(
        username
    )

    if not activities:

        st.info(
            "No activities recorded yet."
        )

        return

    for item in activities:

        left, right = st.columns(
            [8, 1]
        )

        with left:

            st.markdown(
                f"""
                <div class="card">
                    <strong>
                        {safe_text(item["activity_date"])}
                    </strong>
                    <br><br>
                    {safe_text(item["activity"])}
                </div>
                """,
                unsafe_allow_html=True
            )

        with right:

            if st.button(
                "Delete",
                key=f"delete_activity_{item['id']}"
            ):

                delete_activity(
                    item["id"]
                )

                st.rerun()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def admin_dashboard():

    all_projects = get_projects()

    st.markdown(
        '<div class="main-title">DigiOps</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Manager Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")
    st.divider()

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    total_projects = len(all_projects)

    running = sum(
        1
        for p in all_projects
        if p["status"] == "Running"
    )

    completed = sum(
        1
        for p in all_projects
        if p["status"] == "Completed"
    )

    hold = sum(
        1
        for p in all_projects
        if p["status"] == "Hold"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-number">
                    {total_projects}
                </div>
                <div class="metric-label">
                    Total Projects
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-number">
                    {running}
                </div>
                <div class="metric-label">
                    Running
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-number">
                    {completed}
                </div>
                <div class="metric-label">
                    Completed
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-number">
                    {hold}
                </div>
                <div class="metric-label">
                    On Hold
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # --------------------------------------------------------
    # All projects grouped by employee
    # --------------------------------------------------------

    st.subheader(
        "All Employee Projects"
    )

    employee_names = [
        "Farid",
        "Suseendra",
        "Srihari",
        "Rajvineeth"
    ]

    for employee in employee_names:

        employee_projects = [
            p
            for p in all_projects
            if p["username"] == employee
        ]

        st.markdown(
            f"### {employee}"
        )

        if not employee_projects:

            st.caption(
                "No projects created."
            )

            continue

        for project in employee_projects:

            project_id = project["id"]

            st.markdown(
                f"""
                <div class="project-card">
                    <strong>
                        {safe_text(project["project_name"])}
                    </strong>
                    &nbsp;&nbsp;
                    {status_dot(project["status"])}
                    <span>
                        {safe_text(project["status"])}
                    </span>
                    <br>
                    <span style="
                        color:#687987;
                        font-size:13px;
                    ">
                        Project Handler:
                        {safe_text(project["username"])}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                "View Workflow",
                key=f"admin_view_{project_id}",
                use_container_width=True
            ):

                st.session_state.admin_selected_project = project_id

                st.rerun()

    # --------------------------------------------------------
    # Admin workflow view
    # --------------------------------------------------------

    if st.session_state.admin_selected_project:

        admin_workflow_page(
            st.session_state.admin_selected_project
        )


# ============================================================
# ADMIN WORKFLOW VIEW
# ============================================================

def admin_workflow_page(project_id):

    project = get_project(
        project_id
    )

    if not project:
        return

    st.divider()

    st.subheader(
        f"Project Workflow — {project['project_name']}"
    )

    st.write(
        f"Project Handler: "
        f"**{project['username']}**"
    )

    st.write(
        f"Project Status: "
        f"{project['status']}"
    )

    workflow = get_workflow(
        project_id
    )

    completed_count = sum(
        1
        for step in workflow
        if step["completed"]
    )

    total_steps = len(workflow)

    st.progress(
        completed_count / total_steps
        if total_steps
        else 0
    )

    st.write(
        f"**{completed_count} / {total_steps}** "
        f"workflow steps completed."
    )

    st.write("")

    for step in workflow:

        st.markdown(
            f"""
            <div class="workflow-row">
                {workflow_dot(bool(step["completed"]))}
                <span class="workflow-name">
                    <strong>
                        {step["step_number"]}.
                    </strong>
                    {safe_text(step["step_name"])}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.button(
        "Close Workflow"
    ):

        st.session_state.admin_selected_project = None

        st.rerun()


# ============================================================
# LOGOUT
# ============================================================

def logout():

    st.divider()

    if st.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.page = "home"

        st.session_state.selected_date = None
        st.session_state.selected_project = None
        st.session_state.admin_selected_project = None

        st.rerun()


# ============================================================
# MAIN APPLICATION
# ============================================================

if not st.session_state.logged_in:

    login_page()

else:

    # ========================================================
    # ADMIN
    # ========================================================

    if st.session_state.role == "admin":

        admin_dashboard()

        logout()

    # ========================================================
    # EMPLOYEE
    # ========================================================

    else:

        user_navigation()

        if st.session_state.page == "home":

            user_home()

        elif st.session_state.page == "calendar":

            calendar_page()

        elif st.session_state.page == "projects":

            if st.session_state.selected_project:

                project_workflow_page(
                    st.session_state.selected_project
                )

            else:

                projects_page()

        elif st.session_state.page == "activities":

            activities_page()

        logout()

