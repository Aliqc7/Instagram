import numpy as np
import streamlit as st
import flickr

# -------------------Settings---------------

page_title = "Flickr Photo dataset creator"
page_icon = ":camera_with_flash:"
layout = "centered"
dl_path = 'input_photos/'
db_name = "flickr_dataset.db"
dl_path = "input_photos/"
# ---------------------------------------------


st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + "" + page_icon)


# ------------------------------

tag_list = ["Nature", "Animals", "People", "Vehicles", "Food", "Buildings", "Art and Design", "Technology", "Landscape"]
photo_id = 0
with st.container():
    tagger_name = st.text_input("Please write your name here and press Enter", value="Unknown")
    if tagger_name:
        st.write(f"You are tagging as: {tagger_name}")

col1, col2 = st.columns(2)
with col1:
    st.write("Click on the 'show photo' button to see a photo")
    clicked = st.button("Show photo")

    if clicked:
        photo_id, image = flickr.get_photo_for_manual_tagging(db_name, dl_path)
        st.image(image)
        st.write(photo_id)
        with open('current_photo.txt', 'w') as f:
            f.write(f"{photo_id}")

with col2:
    with open('current_photo.txt', 'r') as f:
        photo_id = int(f.read())
    st.write("Please select all relevant tags and click submit")
    with st.form("entry_form", clear_on_submit=True):
        selected_tags = [st.checkbox(tag) for tag in tag_list]
        int_selected_tags = [int(b) for b in selected_tags]
        submitted = st.form_submit_button("Submit")
        if submitted:
            photo_tag_vector_input_list = flickr.create_input_for_manual_tag_photo_vector_table(photo_id, int_selected_tags, tagger_name)
            flickr.add_photo_tags_to_photo_tag_vector_table(photo_tag_vector_input_list, db_name)
            flickr.update_tag_status(photo_id, db_name)
            st.write(f"Successfully uploaded thank you very much {tagger_name}!")



