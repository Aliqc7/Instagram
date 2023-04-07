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
check_box_key = "check_box"
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + "" + page_icon)


def set_new_photo_in_session(streamlit_handle, cursor):
    streamlit_handle.session_state[photo_id] = str(flickr.choose_photo_to_tag_manually_pg(cursor))


@st.cache_resource
def get_secrets():
    return flickr.get_aws_secret_for_db(secret_name, region_name)


@st.cache_resource
def get_db_conn(s):
    cn = flickr.connect_to_postgres_db(s)
    cn.autocommit = True
    return cn


# ------------------------------
secret = get_secrets()
conn = get_db_conn(secret)
c = conn.cursor()
tag_list = flickr.get_tag_list_form_db_pg(c)

show_photo = "show_photo"
should_disable = "should_disable"
photo_id = "photo_id"

def reset_checkbox():
    st.session_state[check_box_key] = False
def run():
    with st.container():
        tagger_name = st.text_input("Please write your name here and press Enter", value="Unknown")
        if tagger_name:
            st.write(f"You are tagging as: {tagger_name}")

    col1, col2 = st.columns(2)
    with col1:
        if photo_id not in st.session_state:
            set_new_photo_in_session(st, c)

        key = f"{st.session_state[photo_id]}.jpg"
        image = flickr.read_image_from_s3(key, bucket_name)
        image = image.resize((500, 500))
        st.image(image)
        st.write(st.session_state[photo_id])

    with col2:
        st.write("Please select all relevant tags and click submit")

        not_applicable = st.checkbox("None of the tags are applicable", value=False, key=check_box_key)

        with st.form("entry_form", clear_on_submit=True):
            n_radio = math.floor(len(tag_list) / 2)
            selected_tags = []
            for i in range(n_radio):
                selected_tag = st.radio(f"{tag_list[2 * i]}/{tag_list[2 * i + 1]}",
                                        [tag_list[2 * i], tag_list[2 * i + 1]], key=i,
                                        disabled=not_applicable)
                selected_tags.append(selected_tag)
            if not_applicable:
                selected_tags = ["NA"]

            submitted = st.form_submit_button("Submit", on_click=reset_checkbox)
            if submitted:
                photo_tag_input_list = flickr.create_input_for_manual_tag_photo_table(st.session_state[photo_id],
                                                                                      selected_tags,
                                                                                      tagger_name, c)
                flickr.add_photo_tags_to_photo_tag_table_pg(photo_tag_input_list, c)
                flickr.update_tag_status_pg(st.session_state[photo_id], c)
                st.write(f"Successfully uploaded! Thank you very much {tagger_name}!")
                set_new_photo_in_session(st, c)
                st.experimental_rerun()


if __name__ == "__main__":
    run()
