import streamlit as st
import flickr
import math
# -------------------Settings---------------

page_title = "Flickr Photo dataset creator"
page_icon = ":camera_with_flash:"
layout = "centered"
dl_path = 'input_photos/'
db_name = "flickr_dataset.db"
dl_path = "input_photos/"
bucket_name = "flickr-input-photos"
# ---------------------------------------------

tag_list = flickr.get_tag_list_form_db(db_name)

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + "" + page_icon)


# ------------------------------

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
        photo_id = flickr.choose_photo_to_tag_manually(db_name)
        #key = f"{photo_id}.jpg"
        #image = flickr.read_image_from_s3(key, bucket_name)
        #TODO change this to read from s3
        image = flickr.get_photo_image(photo_id, dl_path)
        image = image.resize((500, 500))
        st.image(image)
        st.write(photo_id)
        with open('current_photo.txt', 'w') as f:
            f.write(f"{photo_id}")

with col2:
    with open('current_photo.txt', 'r') as f:
        photo_id = int(f.read())
    st.write("Please select all relevant tags and click submit")

    if "disabled" not in st.session_state:
        st.session_state.disabled = False
    not_applicable = st.checkbox("None of the tags are applicable", key="disabled")

    with st.form("entry_form", clear_on_submit=True):
        n_radio = math.floor(len(tag_list) / 2)
        selected_tags = []
        for i in range(n_radio):
            selected_tag = st.radio(f"{tag_list[2*i]}/{tag_list[2*i+1]}", [tag_list[2*i], tag_list[2*i+1]], key=i,
                     disabled=st.session_state.disabled)
            selected_tags.append(selected_tag)
        if not_applicable:
            selected_tags = ["NA"]

        # selected_tags = [st.checkbox(tag) for tag in tag_list]
        # selected_tags_list = [tag for i, tag in enumerate(tag_list) if selected_tags[i] ==True]
        # #int_selected_tags = [int(b) for b in selected_tags]
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(selected_tags)
        #     st.write(selected_tags_list)
        #     photo_tag_input_list = flickr.create_input_for_manual_tag_photo_table(photo_id, selected_tags_list, tagger_name, db_name)
        #     flickr.add_photo_tags_to_photo_tag_table(photo_tag_input_list, db_name)
        #     flickr.update_tag_status(photo_id, db_name)
        #     st.write(f"Successfully uploaded thank you very much {tagger_name}!")



