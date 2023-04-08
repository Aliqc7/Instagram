import streamlit as st
import flickr
import math

# -------------------Settings---------------

page_title = "Manual photo tagging"
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
tagger_name = "tagger_name"


def submit_and_reset(steramlit_handel, sel_tags, cursor):
    photo_tag_input_list = flickr.create_input_for_manual_tag_photo_table(st.session_state[photo_id],
                                                                          sel_tags,
                                                                          st.session_state[tagger_name],
                                                                          cursor)
    flickr.add_photo_tags_to_photo_tag_table_pg(photo_tag_input_list, cursor)
    flickr.update_tag_status_pg(st.session_state[photo_id], cursor)
    set_new_photo_in_session(steramlit_handel, cursor)
    st.session_state[check_box_key] = False

# def reset_checkbox():
#     st.session_state[check_box_key] = False



# def announce_tagger_name():
#     st.write(f"You are tagging as {st.session_state[tagger_name]}!")


def run():
    tab1, tab2 = st.tabs(["Introduction", "Tag photos"])

    with tab1:
        with st.container():
            with st.form("Your name"):
                name = st.text_input("**Please enter your name and click 'Submit'**",
                                     value="Unknown")
                submitted = st.form_submit_button("Submit")
                if submitted:
                    st.session_state[tagger_name] = name
                    st.write(f"**Thank you {st.session_state[tagger_name]}! Please go to 'Tag photos' tab to start tagging.**")

        with st.container():
            st.write("""            
                **What are you helping with?**\n
                Thank you for agreeing to contribute to this project. You will be shown a series of photos, one at a 
                time, and will be asked to tag them. Specifically, you should determine if the photo is taken outdoors 
                or indoors, during the day or the night, includes people, includes pets.\n
                
                I will use the tagged photos later on to train a neural network which will hopefully be able to classify  
                photos that it has never seen before.\n
                
                **Please note the following before starting to tag photos:**\n
                
                - If none of the tags are applicable, e.g., when the image shows a drawing, a sculpture, a dish of food, 
                etc., please check the box 'None of the tags are applicable'.\n
                - Please only consider cats and dogs as pets.\n
                - For indoor photos, if it is not obvious if the it is 'Day' or 'Night, please tag as day.\n
                

            """)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            if tagger_name not in st.session_state:
                st.session_state [tagger_name] = "Unknown"
            st.write(f"**You are tagging as {st.session_state[tagger_name]}.**")
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

                submitted = st.form_submit_button("Submit", on_click=submit_and_reset, kwargs=dict(steramlit_handel=st, sel_tags=selected_tags, cursor=c))
                if submitted:
                    st.write(f"Successfully uploaded! Thank you very much {st.session_state[tagger_name]}!")


if __name__ == "__main__":
    run()
