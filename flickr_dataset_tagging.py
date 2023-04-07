import streamlit as st
import flickr
import math
# -------------------Settings---------------

page_title = "Flickr Photo dataset creator"
page_icon = ":camera_with_flash:"
layout = "centered"
dl_path = 'input_photos/'
bucket_name = "flickr-input-photos"
secret_name = "rds!db-fa439d53-e30b-4b60-9ced-321818cad173"
region_name = "us-east-1"
# ---------------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + "" + page_icon)


# ------------------------------
secret = flickr.get_aws_secret_for_db(secret_name, region_name)
conn = flickr.connect_to_postgres_db(secret)
conn.autocommit = True
c = conn.cursor()
tag_list = flickr.get_tag_list_form_db_pg(c)


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
        photo_id = flickr.choose_photo_to_tag_manually_pg(c)
        key = f"{photo_id}.jpg"
        image = flickr.read_image_from_s3(key, bucket_name)
        #TODO change this to read from s3
        # image = flickr.get_photo_image(photo_id, dl_path)
        image = image.resize((500, 500))
        st.image(image)
        st.write(photo_id)
        with open('current_photo.txt', 'w') as f:
            f.write(f"{photo_id}")

with col2:
    with open('current_photo.txt', 'r') as f:
        photo_id = f.read()
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

        submitted = st.form_submit_button("Submit")
        if submitted:
            photo_tag_input_list = flickr.create_input_for_manual_tag_photo_table(photo_id, selected_tags, tagger_name, c)
            flickr.add_photo_tags_to_photo_tag_table_pg(photo_tag_input_list, c)
            flickr.update_tag_status_pg(photo_id, c)
            st.write(f"Successfully uploaded! Thank you very much {tagger_name}!")



