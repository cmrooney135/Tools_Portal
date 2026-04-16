import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import subprocess



# --- Configuration ---
DATA_DIR = Path("bug_data")
BUGS_FILE = DATA_DIR / "bugs.json"
SUGGESTIONS_FILE = DATA_DIR / "suggestions.json"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
FILES_DIR = DATA_DIR / "files"

ADMIN_PASSWORD = st.secrets["general"]["admin_password"]

# ✅ Add/remove your projects here!
PROJECTS = [
    "FTP Dashboard",
    "Tesla Tools",
    "Paradise Tools",
    "SI Testing",
    "Component Assessment Tool",
]

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)
FILES_DIR.mkdir(exist_ok=True)

# --- Helper Functions ---
def load_bugs():
    if BUGS_FILE.exists():
        with open(BUGS_FILE, "r") as f:
            return json.load(f)
    return []

def save_bugs(bugs):
    """Save bugs to the JSON file and push changes to the remote repository."""
    with open(BUGS_FILE, "w") as f:
        json.dump(bugs, f, indent=2)

    # Automate Git commands
    try:
        # Stage the changes
        subprocess.run(["git", "add", str(BUGS_FILE)], check=True)

        # Commit the changes
        commit_message = f"Bug report updated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push the changes to the remote repository
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"An error occurred while pushing changes to the repository: {e}")


def load_suggestions():
    if SUGGESTIONS_FILE.exists():
        with open(SUGGESTIONS_FILE, "r") as f:
            return json.load(f)
    return []

def save_suggestions(suggestions):
    with open(SUGGESTIONS_FILE, "w") as f:
        json.dump(suggestions, f, indent=2)

def save_screenshots(uploaded_files, item_id, prefix="bug"):
    """Save multiple uploaded screenshots and return a list of file paths."""
    paths = []
    for i, uploaded_file in enumerate(uploaded_files):
        ext = uploaded_file.name.split(".")[-1]
        filename = f"{prefix}_{item_id}_{i+1}.{ext}"
        filepath = SCREENSHOTS_DIR / filename
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        paths.append(str(filepath))
    return paths


def save_supporting_files(uploaded_files, item_id, prefix="bug"):
    """Save multiple uploaded supporting files and return a list of file paths."""
    paths = []
    for i, uploaded_file in enumerate(uploaded_files):
        ext = uploaded_file.name.split(".")[-1]
        filename = f"{prefix}_{item_id}_file_{i+1}.{ext}"
        filepath = FILES_DIR / filename
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        paths.append(str(filepath))
    return paths


def check_admin_auth():
    """Returns True if admin is authenticated."""
    if st.session_state.get("admin_authenticated"):
        return True
    return False

# --- Page Config ---
st.set_page_config(page_title="Carols Tools Portal", page_icon="✨", layout="wide")

# --- Initialize Session State ---
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# --- Sidebar ---
st.sidebar.title("✨ Carols Tools Portal")
st.sidebar.divider()
mode = st.sidebar.radio("Mode", ["📫 Submit Feedback", "🔒 Admin Panel"])

# Show logout button if admin is authenticated
if st.session_state.admin_authenticated and mode == "🔒 Admin Panel":
    st.sidebar.divider()
    st.sidebar.success("✅ Logged in as Admin")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()

# ============================================================
# MODE 1: USER SUBMISSION
# ============================================================
if mode == "📫 Submit Feedback":
    st.title("📫 Submit Feedback")

    tab_bug, tab_suggestion = st.tabs(["🐛 Report a Bug", "💡 Submit a Suggestion"])

    # ----- Tab 1: Report a Bug -----
    with tab_bug:
        st.header("🐛 Report a New Bug")

        with st.form("bug_form", clear_on_submit=True):
            project = st.selectbox("Project *", PROJECTS, key="bug_project")
            reporter_name = st.text_input("Your Name", placeholder="Jane Doe", key="bug_name")
            bug_title = st.text_input(
                "Bug Title *", placeholder="e.g., Login button not working", key="bug_title"
            )
            severity = st.selectbox(
                "Severity", ["🟢 Low", "🟡 Medium", "🔴 High", "🚨 Critical"], key="bug_severity"
            )
            category = st.selectbox(
                "Category",
                ["UI/UX", "Backend", "Functionality", "Logic", "Timing", "Other"],
                key="bug_category",
            )
            description = st.text_area(
                "Describe the Bug *",
                placeholder="Steps to reproduce:\n1. Go to ...\n2. Click on ...\n3. See error ...",
                height=200,
                key="bug_desc",
            )
            screenshot = st.file_uploader(
                "Upload Pictures (optional)",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                accept_multiple_files=True,   
                key="bug_screenshot",
            )
            supporting_files = st.file_uploader(
                "Upload Supporting Files (optional)",
                type=["pdf", "doc", "docx", "xls", "xlsx", "csv", "txt", "log", "json", "xml", "zip", "html", "py", "sql", "md", "pptx"],
                accept_multiple_files=True,
                key="bug_files",
            )


            submitted = st.form_submit_button("🚀 Submit Bug Report")

            if submitted:
                if not bug_title.strip() or not description.strip():
                    st.error("Please fill in the **Bug Title** and **Description**.")
                else:
                    bugs = load_bugs()
                    bug_id = len(bugs) + 1

                    screenshot_paths = []
                    if screenshot:  # screenshot is now a list
                        screenshot_paths = save_screenshots(screenshot, bug_id)

                    file_paths = []
                    if supporting_files:
                        file_paths = save_supporting_files(supporting_files, bug_id)

                    new_bug = {
                        "id": bug_id,
                        "project": project,
                        "reporter": reporter_name or "Anonymous",
                        "title": bug_title,
                        "severity": severity,
                        "category": category, 
                        "description": description,
                        "screenshots": screenshot_paths,
                        "files": file_paths,
                        "status": "Open",
                        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }


                    bugs.append(new_bug)
                    save_bugs(bugs)
                    st.success(
                        f"✅ Bug **#{bug_id}** for **{project}** reported successfully! Thank you, {new_bug['reporter']}!"
                    )

    # ----- Tab 2: Submit a Suggestion -----
    with tab_suggestion:
        st.header("💡 Suggestion Box")

        with st.form("suggestion_form", clear_on_submit=True):
            project = st.selectbox("Project *", PROJECTS, key="sug_project")
            suggester_name = st.text_input("Your Name", placeholder="Jane Doe", key="sug_name")
            suggestion_title = st.text_input(
                "Suggestion Title *",
                placeholder="e.g., Add dark mode support",
                key="sug_title",
            )
            priority = st.selectbox(
                "How important is this to you?",
                [
                    "⭐ Nice to Have",
                    "⭐⭐ Would Be Helpful",
                    "⭐⭐⭐ Really Want This",
                    "⭐⭐⭐⭐ Essential / Dealbreaker",
                ],
                key="sug_priority",
            )
            suggestion_type = st.selectbox(
                "Type",
                [
                    "🆕 New Feature",
                    "🔧 Improvement to Existing Feature",
                    "🎨 Design / UI Change",
                    "⚡ Performance Enhancement",
                    "📖 Documentation",
                    "💬 Other",
                ],
                key="sug_type",
            )
            details = st.text_area(
                "Describe your suggestion *",
                placeholder="e.g., It would be great if we could have a dark mode option in the settings for better night-time usability.",
                height=200,
                key="sug_details",
            )
            screenshot = st.file_uploader(
                "Upload Pictures (optional)",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                accept_multiple_files=True,
                key="sug_screenshot",
            )
            supporting_files = st.file_uploader(
                "Upload Supporting Files (optional)",
                type=["pdf", "doc", "docx", "xls", "xlsx", "csv", "txt", "log", "json", "xml", "zip", "html", "py", "sql", "md", "pptx"],
                accept_multiple_files=True,
                key="sug_files",
            )

            submitted = st.form_submit_button("💡 Submit Suggestion")

            if submitted:
                if not suggestion_title.strip() or not details.strip():
                    st.error("Please fill in the **Title** and **Description**.")
                else:
                    suggestions = load_suggestions()
                    suggestion_id = len(suggestions) + 1

                    screenshot_paths = []
                    if screenshot:
                        screenshot_paths = save_screenshots(screenshot, suggestion_id, prefix="sug")

                    file_paths = []
                    if supporting_files:
                        file_paths = save_supporting_files(supporting_files, suggestion_id, prefix="sug")

                    new_suggestion = {
                        "id": suggestion_id,
                        "project": project,
                        "suggester": suggester_name or "Anonymous",
                        "title": suggestion_title,
                        "priority": priority,
                        "type": suggestion_type,
                        "details": details,
                        "screenshots": screenshot_paths,
                        "files": file_paths,
                        "status": "New",
                        "admin_notes": "",
                        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    suggestions.append(new_suggestion)
                    save_suggestions(suggestions)
                    st.success(
                        f"✅ Suggestion **#{suggestion_id}** submitted! Thank you, {new_suggestion['suggester']}! 💡"
                    )


# ============================================================
# MODE 2: ADMIN PANEL (Password Protected)
# ============================================================
elif mode == "🔒 Admin Panel":
    st.title("🔒 Admin Panel")

    # --- Authentication Gate ---
    if not check_admin_auth():
        st.warning("Please log in to access the admin panel.")

        with st.form("login_form"):
            password_input = st.text_input("Admin Password", type="password")
            login_btn = st.form_submit_button("🔑 Log In")

            if login_btn:
                if password_input == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again.")
        st.stop()

    # --- Admin is authenticated beyond this point ---

    tab_bugs, tab_suggestions = st.tabs(["🐛 Bug Reports", "💡 Suggestions"])

    # ----- Admin Tab 1: Bug Reports -----
    with tab_bugs:
        st.header("All Bug Reports")

        bugs = load_bugs()

        if not bugs:
            st.info("No bugs reported yet. 🎉")
        else:
            col0, col1, col2, col3 = st.columns(4)
            with col0:
                filter_project = st.multiselect("Filter by Project", PROJECTS, key="adm_bug_proj")
            with col1:
                filter_severity = st.multiselect(
                    "Filter by Severity",
                    ["🟢 Low", "🟡 Medium", "🔴 High", "🚨 Critical"],
                    key="adm_bug_sev",
                )
            with col2:
                filter_status = st.multiselect(
                    "Filter by Status",
                    ["Open", "In Progress", "Resolved"],
                    key="adm_bug_stat",
                )
            with col3:
                filter_category = st.multiselect(
                    "Filter by Category",
                    ["UI/UX", "Backend", "Functionality", "Logic", "Timing", "Other"],
                    key="adm_bug_cat",
                )

            filtered = bugs
            if filter_project:
                filtered = [b for b in filtered if b.get("project") in filter_project]
            if filter_severity:
                filtered = [b for b in filtered if b["severity"] in filter_severity]
            if filter_status:
                filtered = [b for b in filtered if b["status"] in filter_status]
            if filter_category:
                filtered = [b for b in filtered if b["category"] in filter_category]

            # --- Stats ---
            st.divider()
            stat_cols = st.columns(4)
            total_open = sum(1 for b in bugs if b["status"] == "Open")
            total_in_progress = sum(1 for b in bugs if b["status"] == "In Progress")
            total_resolved = sum(1 for b in bugs if b["status"] == "Resolved")
            with stat_cols[0]:
                st.metric("Total Bugs", len(bugs))
            with stat_cols[1]:
                st.metric("🟠 Open", total_open)
            with stat_cols[2]:
                st.metric("🔵 In Progress", total_in_progress)
            with stat_cols[3]:
                st.metric("✅ Resolved", total_resolved)

            st.markdown(f"**Showing {len(filtered)} of {len(bugs)} bugs**")
            st.divider()

            for bug in reversed(filtered):
                project_label = bug.get("project", "Unknown Project")
                with st.expander(
                    f"**#{bug['id']}** — [{project_label}] {bug['title']}  |  {bug['severity']}  |  Status: {bug['status']}"
                ):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.markdown(f"**Project:** {project_label}")
                        st.markdown(f"**Reporter:** {bug['reporter']}")
                        st.markdown(f"**Category:** {bug['category']}")
                        st.markdown(f"**Submitted:** {bug['submitted_at']}")
                        st.markdown("---")
                        st.markdown(f"**Description:**\n\n{bug['description']}")
                    with col_b:
                        screenshots = bug.get("screenshots", [])
                        # Backwards compatible with old single-screenshot bugs
                        if not screenshots and bug.get("screenshot"):
                            screenshots = [bug["screenshot"]]
                        
                        if screenshots:
                            for img_path in screenshots:
                                if os.path.exists(img_path):
                                    st.image(img_path, caption=os.path.basename(img_path), use_container_width=True)
                        else:
                            st.markdown("*No screenshots attached.*")

                        files = bug.get("files", [])
                        if files:
                            st.markdown("**Supporting Files:**")
                            for file_path in files:
                                if os.path.exists(file_path):
                                    with open(file_path, "rb") as f:
                                        st.download_button(
                                            label=f"📎 {os.path.basename(file_path)}",
                                            data=f,
                                            file_name=os.path.basename(file_path),
                                            key=f"dl_bug_{bug['id']}_{os.path.basename(file_path)}",
                                        )


                    new_status = st.selectbox(
                        "Update Status",
                        ["Open", "In Progress", "Resolved"],
                        index=["Open", "In Progress", "Resolved"].index(bug["status"]),
                        key=f"adm_bug_status_{bug['id']}",
                    )
                    if new_status != bug["status"]:
                        bug["status"] = new_status
                        save_bugs(bugs)
                        st.success(f"Bug #{bug['id']} updated to **{new_status}**!")
                        st.rerun()
                    # --- Delete Bug ---
                    st.markdown("---")
                    col_del1, col_del2 = st.columns([3, 1])
                    with col_del2:
                        confirm_delete = st.checkbox("Confirm deletion", key=f"confirm_del_bug_{bug['id']}")
                        if confirm_delete:
                            if st.button("🗑️ Delete Bug", key=f"del_bug_{bug['id']}", type="primary"):
                                # Remove screenshot files
                                screenshots = bug.get("screenshots", [])
                                if not screenshots and bug.get("screenshot"):
                                    screenshots = [bug["screenshot"]]
                                for img_path in screenshots:
                                    if os.path.exists(img_path):
                                        os.remove(img_path)
                                for file_path in bug.get("files", []):
                                    if os.path.exists(file_path):
                                        os.remove(file_path)

                                # Remove bug from list and save
                                bugs.remove(bug)
                                save_bugs(bugs)
                                st.success(f"Bug #{bug['id']} deleted!")
                                st.rerun()
                    with col_del1:
                        if not confirm_delete:
                            st.caption("🔒 Check 'Confirm deletion' to enable the delete button.")
                        

    # ----- Admin Tab 2: Suggestions -----
    with tab_suggestions:
        st.header("💡 All Suggestions")

        suggestions = load_suggestions()

        if not suggestions:
            st.info("No suggestions yet. Share the link so people can submit ideas! 💡")
        else:
            col0, col1, col2 = st.columns(3)
            with col0:
                filter_project = st.multiselect(
                    "Filter by Project", PROJECTS, key="adm_sug_proj"
                )
            with col1:
                filter_type = st.multiselect(
                    "Filter by Type",
                    [
                        "🆕 New Feature",
                        "🔧 Improvement to Existing Feature",
                        "🎨 Design / UI Change",
                        "⚡ Performance Enhancement",
                        "📖 Documentation",
                        "💬 Other",
                    ],
                    key="adm_sug_type",
                )
            with col2:
                filter_status = st.multiselect(
                    "Filter by Status",
                    ["New", "Under Review", "Planned", "In Progress", "Implemented", "Declined"],
                    key="adm_sug_stat",
                )

            filtered = suggestions
            if filter_project:
                filtered = [s for s in filtered if s.get("project") in filter_project]
            if filter_type:
                filtered = [s for s in filtered if s["type"] in filter_type]
            if filter_status:
                filtered = [s for s in filtered if s["status"] in filter_status]

            # --- Stats ---
            st.divider()
            status_counts = {}
            for s in suggestions:
                status_counts[s["status"]] = status_counts.get(s["status"], 0) + 1
            stat_cols = st.columns(len(status_counts) if status_counts else 1)
            for i, (status, count) in enumerate(status_counts.items()):
                with stat_cols[i]:
                    st.metric(status, count)

            st.markdown(f"**Showing {len(filtered)} of {len(suggestions)} suggestions**")
            st.divider()

            for sug in reversed(filtered):
                project_label = sug.get("project", "Unknown Project")
                with st.expander(
                    f"**#{sug['id']}** — [{project_label}] {sug['title']}  |  {sug['type']}  |  Status: {sug['status']}"
                ):
                    st.markdown(f"**Project:** {project_label}")
                    st.markdown(f"**Submitted by:** {sug['suggester']}")
                    st.markdown(f"**Priority:** {sug['priority']}")
                    st.markdown(f"**Type:** {sug['type']}")
                    st.markdown(f"**Submitted:** {sug['submitted_at']}")
                    st.markdown("---")
                    st.markdown(f"**Details:**\n\n{sug['details']}")

                    screenshots = sug.get("screenshots", [])
                    if screenshots:
                        st.markdown("**Screenshots:**")
                        for img_path in screenshots:
                            if os.path.exists(img_path):
                                st.image(img_path, caption=os.path.basename(img_path), use_container_width=True)
                    else:
                        st.markdown("*No screenshots attached.*")

                    files = sug.get("files", [])
                    if files:
                        st.markdown("**Supporting Files:**")
                        for file_path in files:
                            if os.path.exists(file_path):
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        label=f"📎 {os.path.basename(file_path)}",
                                        data=f,
                                        file_name=os.path.basename(file_path),
                                        key=f"dl_sug_{sug['id']}_{os.path.basename(file_path)}",
                                    )

                    st.markdown("---")

                    new_status = st.selectbox(
                        "Update Status",
                        [
                            "New",
                            "Under Review",
                            "Planned",
                            "In Progress",
                            "Implemented",
                            "Declined",
                        ],
                        index=[
                            "New",
                            "Under Review",
                            "Planned",
                            "In Progress",
                            "Implemented",
                            "Declined",
                        ].index(sug["status"]),
                        key=f"adm_sug_status_{sug['id']}",
                    )

                    admin_notes = st.text_area(
                        "Admin Notes (only visible here)",
                        value=sug.get("admin_notes", ""),
                        key=f"adm_sug_notes_{sug['id']}",
                        placeholder="e.g., Good idea — planning for v2.0",
                    )

                    if new_status != sug["status"] or admin_notes != sug.get("admin_notes", ""):
                        sug["status"] = new_status
                        sug["admin_notes"] = admin_notes
                        save_suggestions(suggestions)
                        st.success(f"Suggestion #{sug['id']} updated!")
                        st.rerun()
                        # --- Delete Suggestion ---
                    st.markdown("---")
                    col_del1, col_del2 = st.columns([3, 1])
                    with col_del2:
                        confirm_delete = st.checkbox("Confirm deletion", key=f"confirm_del_sug_{sug['id']}")
                        if confirm_delete:
                            if st.button("🗑️ Delete Suggestion", key=f"del_sug_{sug['id']}", type="primary"):
                                # Remove screenshot files
                                for img_path in sug.get("screenshots", []):
                                    if os.path.exists(img_path):
                                        os.remove(img_path)
                                for file_path in sug.get("files", []):
                                    if os.path.exists(file_path):
                                        os.remove(file_path)
                                suggestions.remove(sug)
                                save_suggestions(suggestions)
                                st.success(f"Suggestion #{sug['id']} deleted!")
                                st.rerun()
                    with col_del1:
                        if not confirm_delete:
                            st.caption("🔒 Check 'Confirm deletion' to enable the delete button.")

# ============================================================
# FOOTER: Contact Info
# ============================================================
st.sidebar.divider()
st.sidebar.markdown("#### 📬 Contact Me")
st.sidebar.markdown(
    """
    Need direct help?

    [![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/1234567890)

    📱 **+1 (401) 524-2552**
    """
)

