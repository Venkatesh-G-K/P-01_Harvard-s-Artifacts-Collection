import streamlit as st
import pandas as pd
import requests
from sqlalchemy import create_engine

# ==============================
# CONFIG
# ==============================

API_KEY = "99f759b9-4e2f-46d1-9d55-92978f007201"

url = "https://api.harvardartmuseums.org/object"

# ✅ FIXED ENGINE STRING

engine = create_engine(
    "mysql+mysqlconnector://"
    "3fCAZkkCNgfMxEa.root:"
    "h8F1E28rdnGOgobd@"
    "gateway01.ap-southeast-1.prod.aws.tidbcloud.com:"
    "4000/"
    "P1_Harvard_Artifacts"
)

# ==============================
# PAGE TITLE & STYLING (INSERT HERE)
# ==============================

st.set_page_config(page_title="Harvard Artifacts Explorer", layout="wide")

# 🎨 INSERT BACKGROUND STYLING HERE
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f172a; 
        color: #f8fafc; 
    }
    h1, h2, h3 {
        color: #e2e8f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================
# PAGE TITLE
# ==============================

st.title("🏛️ Harvard Artifacts Collection Explorer")

st.write("""
✔ Collect artifact data  
✔ Store into SQL  
✔ Run SQL Queries  
✔ Explore Museum Data
""")

# ==============================
# CLASSIFICATION DROPDOWN
# ==============================

classification = st.selectbox(
    "Select Classification",
    ["Coins", "Paintings", "Sculpture", "Drawings"]
)

# ==============================
# FETCH DATA FUNCTION
# ==============================

def fetch_data(classification):

    all_records = []
    page = 1

    while len(all_records) < 2500:

        params = {
            "apikey": API_KEY,
            "classification": classification,
            "page": page,
            "size": 100
        }

        response = requests.get(url, params=params)

        data = response.json()

        records = data["records"]

        if not records:
            break

        all_records.extend(records)

        page += 1

    return all_records


# ==============================
# DATAFRAME BUILDERS
# ==============================

def create_dataframes(all_records):

    metadata_rows = []
    media_rows = []
    color_rows = []

    for item in all_records:

        metadata_rows.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "culture": item.get("culture"),
            "period": item.get("period"),
            "century": item.get("century"),
            "medium": item.get("medium"),
            "dimensions": item.get("dimensions"),
            "description": item.get("description"),
            "department": item.get("department"),
            "classification": item.get("classification"),
            "accessionyear": item.get("accessionyear"),
            "accessionmethod": item.get("accessionmethod")
        })

        media_rows.append({
            "objectid": item.get("objectid"),
            "imagecount": item.get("imagecount"),
            "mediacount": item.get("mediacount"),
            "colorcount": item.get("colorcount"),
            "rank": item.get("rank"),
            "datebegin": item.get("datebegin"),
            "dateend": item.get("dateend")
        })

        colors = item.get("colors")

        if colors:

            for color in colors:

                color_rows.append({
                    "objectid": item.get("objectid"),
                    "color": color.get("color"),
                    "spectrum": color.get("spectrum"),
                    "hue": color.get("hue"),
                    "percent": color.get("percent"),
                    "css3": color.get("css3")
                })

    metadata_df = pd.DataFrame(metadata_rows)
    media_df = pd.DataFrame(media_rows)
    colors_df = pd.DataFrame(color_rows)

    return metadata_df, media_df, colors_df


# ==============================
# BUTTONS
# ==============================

if st.button("📥 Collect Data"):

    st.write("Fetching data...")

    all_records = fetch_data(classification)

    st.session_state["records"] = all_records

    st.success(f"Collected {len(all_records)} records")


if st.button("👀 Show Data"):

    if "records" in st.session_state:

        df = pd.DataFrame(st.session_state["records"])

        st.dataframe(df.head())

    else:

        st.warning("Collect data first.")


if st.button("💾 Insert into SQL"):

    if "records" in st.session_state:

        metadata_df, media_df, colors_df = create_dataframes(
            st.session_state["records"]
        )

        # ✅ Use append (not replace)

        metadata_df.to_sql(
            "artifact_metadata",
            engine,
            if_exists="append",
            index=False
        )

        media_df.to_sql(
            "artifact_media",
            engine,
            if_exists="append",
            index=False
        )

        colors_df.to_sql(
            "artifact_colors",
            engine,
            if_exists="append",
            index=False
        )

        st.success("Data inserted into SQL successfully")

    else:

        st.warning("Collect data first.")


# ==============================
# QUERY SECTION
# ==============================

st.subheader("🔍 SQL Query Explorer")

queries = {
    # ==============================
    # 🏛️ artifact_metadata Queries (1-5)
    # ==============================
    "1. Artifacts from 11th Century & Byzantine Culture": """
        SELECT id, title, culture, century 
        FROM artifact_metadata 
        WHERE century = '11th century' AND culture = 'Byzantine';
    """,
    "2. Unique Cultures Represented": """
        SELECT DISTINCT culture 
        FROM artifact_metadata 
        WHERE culture IS NOT NULL;
    """,
    "3. Artifacts from the Archaic Period": """
        SELECT id, title, period, classification 
        FROM artifact_metadata 
        WHERE period = 'Archaic';
    """,
    "4. Artifacts Ordered by Accession Year (DESC)": """
        SELECT title, accessionyear, classification 
        FROM artifact_metadata 
        WHERE accessionyear IS NOT NULL 
        ORDER BY accessionyear DESC;
    """,
    "5. Artifact Count per Department": """
        SELECT department, COUNT(*) AS total_artifacts 
        FROM artifact_metadata 
        GROUP BY department 
        ORDER BY total_artifacts DESC;
    """,

    # ==============================
    # 🖼️ artifact_media Queries (6-10)
    # ==============================
    "6. Artifacts with More than 1 Image": """
        SELECT objectid, imagecount 
        FROM artifact_media 
        WHERE imagecount > 1;
    """,
    "7. Average Rank of All Artifacts": """
        SELECT AVG(rank) AS average_rank 
        FROM artifact_media;
    """,
    "8. Artifacts with Higher Colorcount than Mediacount": """
        SELECT objectid, colorcount, mediacount 
        FROM artifact_media 
        WHERE colorcount > mediacount;
    """,
    "9. Artifacts Created Between 1500 and 1600": """
        SELECT objectid, datebegin, dateend 
        FROM artifact_media 
        WHERE datebegin >= 1500 AND dateend <= 1600;
    """,
    "10. Artifacts with No Media Files": """
        SELECT COUNT(*) AS artifacts_with_no_media 
        FROM artifact_media 
        WHERE mediacount = 0 OR mediacount IS NULL;
    """,

    # ==============================
    # 🎨 artifact_colors Queries (11-15)
    # ==============================
    "11. Distinct Hues Used in Dataset": """
        SELECT DISTINCT hue 
        FROM artifact_colors 
        WHERE hue IS NOT NULL;
    """,
    "12. Top 5 Most Used Colors by Frequency": """
        SELECT color, COUNT(*) AS frequency 
        FROM artifact_colors 
        GROUP BY color 
        ORDER BY frequency DESC 
        LIMIT 5;
    """,
    "13. Average Coverage Percentage for Each Hue": """
        SELECT hue, AVG(percent) AS avg_coverage_percentage 
        FROM artifact_colors 
        WHERE hue IS NOT NULL 
        GROUP BY hue 
        ORDER BY avg_coverage_percentage DESC;
    """,
    "14. List All Colors for a Specific Artifact ID": """
        SELECT objectid, color, hue, percent 
        FROM artifact_colors 
        WHERE objectid = (SELECT MIN(objectid) FROM artifact_colors);
    """,
    "15. Total Number of Color Entries": """
        SELECT COUNT(*) AS total_color_entries 
        FROM artifact_colors;
    """,

    # ==============================
    # 🔗 Join-Based Queries (16-20)
    # ==============================
    "16. Titles & Hues for Byzantine Culture": """
        SELECT m.title, c.hue 
        FROM artifact_metadata m 
        JOIN artifact_colors c ON m.id = c.objectid 
        WHERE m.culture = 'Byzantine';
    """,
    "17. Artifact Title with Associated Hues": """
        SELECT m.title, c.hue, c.color 
        FROM artifact_metadata m 
        JOIN artifact_colors c ON m.id = c.objectid;
    """,
    "18. Titles, Cultures, & Ranks (Period Not Null)": """
        SELECT m.title, m.culture, me.rank, m.period 
        FROM artifact_metadata m 
        JOIN artifact_media me ON m.id = me.objectid 
        WHERE m.period IS NOT NULL;
    """,
    "19. Top 10 Ranked Artifacts Including 'Grey' Hue": """
        SELECT DISTINCT m.title, me.rank, c.hue 
        FROM artifact_metadata m 
        JOIN artifact_media me ON m.id = me.objectid 
        JOIN artifact_colors c ON m.id = c.objectid 
        WHERE c.hue = 'Grey' AND me.rank <= 10;
    """,
    "20. Artifact Count & Avg Media Count per Classification": """
        SELECT m.classification, COUNT(m.id) AS total_artifacts, AVG(me.mediacount) AS avg_media_count 
        FROM artifact_metadata m 
        LEFT JOIN artifact_media me ON m.id = me.objectid 
        GROUP BY m.classification;
    """,

    # ==============================
    # 🚀 Custom / Additional Insights Queries (21-25)
    # ==============================
    "21. Custom: Most Common Accession Methods": """
        SELECT accessionmethod, COUNT(*) AS total 
        FROM artifact_metadata 
        WHERE accessionmethod IS NOT NULL 
        GROUP BY accessionmethod 
        ORDER BY total DESC;
    """,
    "22. Custom: Artifacts with Maximum Images": """
        SELECT m.title, me.imagecount 
        FROM artifact_metadata m 
        JOIN artifact_media me ON m.id = me.objectid 
        ORDER BY me.imagecount DESC 
        LIMIT 10;
    """,
    "23. Custom: Dominant Hues Distribution Across Dataset": """
        SELECT hue, COUNT(*) AS hue_count 
        FROM artifact_colors 
        WHERE hue IS NOT NULL 
        GROUP BY hue 
        ORDER BY hue_count DESC;
    """,
    "24. Custom: Century-wise Breakdown of Artifact Collections": """
        SELECT century, COUNT(*) AS artifact_count 
        FROM artifact_metadata 
        WHERE century IS NOT NULL 
        GROUP BY century 
        ORDER BY artifact_count DESC;
    """,
    "25. Custom: Artifacts with Highest Color Diversity (Color Count)": """
        SELECT m.title, me.colorcount 
        FROM artifact_metadata m 
        JOIN artifact_media me ON m.id = me.objectid 
        WHERE me.colorcount IS NOT NULL 
        ORDER BY me.colorcount DESC 
        LIMIT 10;
    """
}

selected_query = st.selectbox(
    "Choose Query",
    list(queries.keys())
)

if st.button("▶ Run Query"):

    query = queries[selected_query]

    result = pd.read_sql(query, engine)

    st.dataframe(result)
