import streamlit as st
import flickr

# -------------------Settings---------------

page_title = "Flickr Photo Finder"
page_icon = ":camera_with_flash:"
layout = "centered"
dl_path = 'flickr_photo_dl/'
# ---------------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + "" + page_icon)


# ------------------------------

st.header("Select a tag")
tag_list = flickr.get_tag_list_form_db()
tag = st.selectbox("1", tag_list)

"---"
with st.form("entry_form", clear_on_submit=True):
    submitted = st.form_submit_button("Find photo")
    if submitted:
        photo_ids = flickr.find_photo_ids_for_tag(tag)
        photo_id = photo_ids[0]
        image = flickr.get_photo_image(photo_id, dl_path)
        st.image(image)