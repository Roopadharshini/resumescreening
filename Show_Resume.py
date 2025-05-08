import streamlit as st
import pymongo
import base64

# Set page config
st.set_page_config(page_title="View Resumes", page_icon="📂")

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["resume_db"]
resumes_collection = db["resumes"]

# Custom CSS for resume viewer
st.markdown("""
<style>
    .resume-viewer {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .candidate-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
        margin-bottom: 15px;
    }
    .filter-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .status-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    .status-high {
        background-color: #e3f9e5;
        color: #1b9e3e;
    }
    .status-medium {
        background-color: #fff8e1;
        color: #ff9800;
    }
</style>
""", unsafe_allow_html=True)

st.title("📂 Candidate Database")

# Filters with improved layout
with st.container():
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Search Filters")
    col1, col2 = st.columns(2)
    with col1:
        position = st.selectbox(
            "Position",
            options=["All"] + sorted(resumes_collection.distinct("position")),
            help="Filter by job position"
        )
    with col2:
        min_score = st.slider("Minimum Score", 0, 100, 70, 
                            help="Set minimum AI match score")
    st.markdown('</div>', unsafe_allow_html=True)

# Query and display results
query = {"llm_score": {"$gte": min_score}}
if position != "All":
    query["position"] = position

resumes = list(resumes_collection.find(query).sort("llm_score", pymongo.DESCENDING))

if resumes:
    st.markdown(f"**Found {len(resumes)} candidates**")
    
    for resume in resumes:
        with st.expander(f"👤 {resume['name']} - {resume['llm_score']}/100", expanded=False):
            st.markdown('<div class="resume-viewer">', unsafe_allow_html=True)
            
            # Header with score and actions
            status_class = "status-high" if resume['llm_score'] >= 80 else "status-medium"
            st.markdown(f"""
            <div class="candidate-header">
                <div>
                    <strong>Position:</strong> {resume['position'].title()}
                    <span style="margin: 0 10px">•</span>
                    <strong>Applied:</strong> {resume['processed_at'].strftime('%b %d, %Y')}
                </div>
                <div>
                    <span class="status-badge {status_class}">
                        {resume['llm_score']}/100
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            cols = st.columns([4, 1])
            with cols[0]:
                # Contact info
                st.markdown("### 📌 Contact Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Email:** {resume.get('email', 'N/A')}")
                with col2:
                    st.markdown(f"**Phone:** {resume.get('phone', 'N/A')}")
                
                # Education
                st.markdown("### 🎓 Education")
                st.write(resume.get('education', 'N/A'))
                
                # Experience
                st.markdown("### 💼 Experience")
                st.write(resume.get('experience', 'N/A'))
                
                # Skills
                st.markdown("### 🛠️ Skills")
                st.write(resume.get('skills', 'N/A'))
                
                # AI Assessment
                st.markdown("### 🤖 AI Assessment")
                st.info(resume.get('summary', 'No summary available'))
            
            with cols[1]:
                # Action buttons
                st.download_button(
                    "📥 Download Resume",
                    data=resume["resume"],
                    file_name=f"{resume['name']}_resume.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                if st.button("👀 View Resume", key=f"view_{resume['_id']}", use_container_width=True):
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64.b64encode(resume["resume"]).decode("utf-8")}" width="700" height="1000" style="border: none;"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                
                if st.button("⭐ Shortlist", key=f"shortlist_{resume['_id']}", use_container_width=True):
                    st.success(f"{resume['name']} added to shortlist!")
            
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("No resumes match the selected criteria")