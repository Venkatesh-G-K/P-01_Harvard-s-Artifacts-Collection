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

"Unique Cultures":
"""
SELECT DISTINCT culture
FROM artifact_metadata;
""",

"Artifacts per Department":
"""
SELECT department, COUNT(*)
FROM artifact_metadata
GROUP BY department;
""",

"Top 5 Colors":
"""
SELECT color, COUNT(*) AS frequency
FROM artifact_colors
GROUP BY color
ORDER BY frequency DESC
LIMIT 5;
""",

"Artifacts with Multiple Images":
"""
SELECT *
FROM artifact_media
WHERE imagecount > 1;
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
