import streamlit as st
import base64
from bokeh.io import export_svgs, export_png
import os
import io

from deepmip_modules import get_csv_data


def init_widgets_single_site(page):
    # initialise user input widgets
    with st.form(key="my_form"):
        # some settings that depend on the current page
        if page == "extract_data":
            st.info(
                """
                Select the present-day location of your site and the variable you are interested in.
                """
            )
            button_label = "GET MODEL DATA"
        elif page == "plot_local":
            st.info(
                """
                Select the present-day location of your site and the variable you are interested in.
                """
            )
            button_label = "UPDATE FIGURES"
        elif page == "plot_map":
            st.info(
                """
                Select the present-day location of your site and an optional label.
                """
            )
            button_label = "UPDATE MAPS"

        col1a, col1b, col1c, col1d = st.columns(4)

        with col1a:
            # use default value if input has not been defined before
            if "modern_lat" not in st.session_state:
                st.session_state.modern_lat = 52.4
            modern_lat = st.number_input(
                label="modern latitude of site",
                min_value=-90.0,
                max_value=90.0,
                step=1.0,
                format="%.1f",
                key="modern_lat",
            )

        with col1b:
            if "modern_lon" not in st.session_state:
                st.session_state.modern_lon = 11.8
            modern_lon = st.number_input(
                label="modern longitude of site",
                min_value=-180.0,
                max_value=180.0,
                step=1.0,
                format="%.1f",
                key="modern_lon",
            )

        with col1c:
            variable_list = [
                "Near-Surface Air Temperature",
                "Sea Surface Temperature",
                "Precipitation",
            ]
            if "user_variable" not in st.session_state:
                st.session_state.user_variable = "Near-Surface Air Temperature"
            user_variable = st.selectbox(
                label="variable",
                options=variable_list,
                key="user_variable",
            )

        with col1d:
            if "user_site_name" not in st.session_state:
                st.session_state.user_site_name = "Store Bælt (Denmark) "
            user_site_name = st.text_input(
                label="OPTIONAL: name of site",
                key="user_site_name",
            )

        # add optional proxy comparison to user input
        if page == "plot_local":
            col2a, col2b, col2c = st.columns(3)

            with col2a:
                st.write("compare to proxy?")
                if "proxy_check" in st.session_state:
                    proxy_check = st.checkbox(label=" ", key="proxy_check")
                else:
                    proxy_check = st.checkbox(label=" ", key="proxy_check", value=True)

            with col2b:
                if "proxy_mean" not in st.session_state:
                    st.session_state.proxy_mean = 26.6
                proxy_mean = st.number_input(
                    label="proxy mean",
                    step=1.0,
                    format="%.1f",
                    key="proxy_mean",
                )

            with col2c:
                if "proxy_std" not in st.session_state:
                    st.session_state.proxy_std = 2.85
                proxy_std = st.number_input(
                    label="proxy uncertainty",
                    step=1.0,
                    format="%.1f",
                    key="proxy_std",
                )

        submit_button = st.form_submit_button(
            label=button_label, use_container_width=True, type="primary"
        )

    if page == "extract_data":
        return (modern_lat, modern_lon, user_variable, user_site_name)
    elif page == "plot_local":
        return (
            modern_lat,
            modern_lon,
            user_variable,
            user_site_name,
            proxy_check,
            proxy_mean,
            proxy_std,
        )
    elif page == "plot_map":
        return (modern_lat, modern_lon, user_site_name)


def reset_csv_data():
    # delete previous input from session state
    if "csv_input" in st.session_state:
        del st.session_state["csv_input"]
    if "site_name" in st.session_state:
        del st.session_state["site_name"]


def init_widgets_multi_site(page):
    # some settings that depend on the current page
    if page == "extract_data":
        csv_proxy_flag = False
        csv_placeholder = "name, modern latitude, modern longitude"
        button_label = "GET MODEL DATA"
    elif page == "plot_local":
        csv_proxy_flag = True
        csv_placeholder = "name, modern latitude, modern longitude, proxy mean (OPTIONAL), proxy uncertainty (OPTIONAL)"
        button_label = "UPDATE FIGURES"
    elif page == "plot_map":
        csv_proxy_flag = False
        csv_placeholder = "name, modern latitude, modern longitude"
        button_label = "UPDATE MAPS"

    st.info(
        """
        Enter the names and present-day locations of your sites in the text box below. 
        Or you can use the dropdown menu below to pick a selection of sites from the DeepMIP compilation.
        """
    )
    template_list = [
        "Enter your own data",
        "DeepMIP marine proxies (latest Paleocene)",
        "DeepMIP marine proxies (Paleocene–Eocene Thermal Maximum)",
        "DeepMIP marine proxies (early Eocene Climatic Optimum)",
        "DeepMIP marine proxies (all time periods)",
        "DeepMIP terrestrial proxies (latest Paleocene)",
        "DeepMIP terrestrial proxies (Paleocene–Eocene Thermal Maximum)",
        "DeepMIP terrestrial proxies (early Eocene Climatic Optimum)",
        "DeepMIP terrestrial proxies (all time periods)",
        "DeepMIP marine+terrestrial proxies  (latest Paleocene)",
        "DeepMIP marine+terrestrial proxies  (Paleocene–Eocene Thermal Maximum)",
        "DeepMIP marine+terrestrial proxies  (early Eocene Climatic Optimum)",
        "DeepMIP marine+terrestrial proxies (all time periods)",
    ]

    csv_choice = st.selectbox(
        label="Choose a template from the DeepMIP proxy compilation or enter your own data:",
        options=template_list,
        key="csv_choice",
        on_change=reset_csv_data,
    )

    if "csv_input" not in st.session_state:
        st.session_state.csv_input = get_csv_data(csv_choice, csv_proxy_flag)

    # initialise user input widgets
    with st.form(key="my_form"):
        csv_input = st.text_area(
            label="Enter your data below (CSV format)",
            # value=csv_data,
            placeholder=csv_placeholder,
            height=200,
            key="csv_input",
        )

        variable_list = [
            "Near-Surface Air Temperature",
            "Sea Surface Temperature",
            "Precipitation",
        ]

        user_variable = st.selectbox(
            label="variable",
            options=variable_list,
            key="user_variable",
        )

        submit_button = st.form_submit_button(
            label=button_label, use_container_width=True, type="primary"
        )

    if page == "plot_map":
        return (csv_choice, csv_input)
    else:
        return (csv_choice, csv_input, user_variable)


def get_base64(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def add_logo():
    bin_str = get_base64("img/deepmip_logo.png")
    # bin_str = get_base64('deepmip_banner2.jpg')

    page_bg_img = (
        """
    <style>
        [data-testid="stSidebarNav"] {
            background-image: url("data:image/png;base64,%s");
            background-repeat: no-repeat;
            padding-top: 115px;
            background-position: 70px 30px;
            background-size: 150px 150px;
        }
        [data-testid="stSidebarNav"]::before {
            content: "DeepMIP-Eocene Database";
            margin-left: 22px;
            margin-top: 20px;
            font-size:22px;
            position: relative;
            top: 90px;
        }
    </style>
    """
        % bin_str
    )
    st.markdown(page_bg_img, unsafe_allow_html=True)


def init_sidebar():
    add_logo()

    css = """
    <style>
        [data-testid='stSidebarNav'] > ul {
            min-height: 330px;
        }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    st.sidebar.success("How to Get Started")
    st.sidebar.markdown(
        """
        1. ☝️ Use the navigation above to select the page of your choice. 
        2. Select the present-day location of your site(s) and the variable you are 
        interested in.
        3. Optionally, you can add a proxy estimate for quick comparison with 
        the model data. 
        4. Click the red button below the form and wait for the results to update.
        """
    )

    st.sidebar.subheader("Links")
    st.sidebar.markdown(
        "Get the code: [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/sebsteinig/deepmip_database_app)",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        # "Get in touch: [![Repo](https://badgen.net/badge/icon/sebsteinig?icon=twitter&label)](https://twitter.com/sebsteinig)",
        "Get in touch: [![Repo](https://badgen.net/badge/icon/email?icon=telegram&label)](mailto:d.j.lunt@bristol.ac.uk)",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        # "Get more info: [www.deepmip.org](https://www.deepmip.org)",
        "Get more info: [![Repo](https://badgen.net/badge/icon/deepmip.org?icon=chrome&label)](https://www.deepmip.org)",
        unsafe_allow_html=True,
    )


def delete_figures(file1, file2, file3):
    for file in [file1, file2, file3]:
        if os.path.exists(file):
            os.remove(file)


def customDownloadButton_JPG_PNG_PDF(figure, filename):
    if "single_map" not in st.session_state:
        # if st.session_state.get('single_map') != True:

        button_map = st.button(
            "Download Map", type="primary", use_container_width=True, key=filename
        )

        st.session_state["single_map"] = button_map  # Saved the state

    print(st.session_state["single_map"])
    st.stop()

    if st.session_state["single_map"] == True:
        progress_bar = st.progress(0)

        progress_bar.progress(1 / 3, "Creating JPG")
        fn3 = filename + ".jpg"
        img3 = io.BytesIO()
        figure.savefig(img3, format="jpg", dpi=200)

        progress_bar.progress(2 / 3, "Creating PNG")
        fn = filename + ".png"
        img = io.BytesIO()
        figure.savefig(img, format="png", dpi=300)

        progress_bar.progress(3 / 3, "Creating PDF")
        fn2 = filename + ".pdf"
        img2 = io.BytesIO()
        figure.savefig(img2, format="pdf")

        progress_bar.empty()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="Download JPG",
                data=img3,
                file_name=fn3,
                mime="image/jpg",
                use_container_width=True,
            )

        with col2:
            st.download_button(
                label="Download PNG",
                data=img,
                file_name=fn,
                mime="image/png",
                use_container_width=True,
            )

        with col3:
            st.download_button(
                label="Download PDF",
                data=img2,
                file_name=fn2,
                mime="image/pdf",
                use_container_width=True,
            )


def customDownloadButton_JPG_PNG(figure, filename):
    if "model_maps" not in st.session_state:
        # if st.session_state.get('model_maps') != True:

        button_models = st.button(
            "Download Model Maps",
            type="primary",
            use_container_width=True,
            key=filename,
        )

        st.session_state["model_maps"] = button_models  # Saved the state

    if st.session_state["model_maps"] == True:
        progress_bar = st.progress(0)

        progress_bar.progress(1 / 2, "Creating JPG")
        fn3 = filename + ".jpg"
        img3 = io.BytesIO()
        figure.savefig(img3, format="jpg", dpi=200)

        progress_bar.progress(1 / 2, "Creating PNG")
        fn = filename + ".png"
        img = io.BytesIO()
        figure.savefig(img, format="png", dpi=300)

        progress_bar.empty()

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download JPG",
                data=img3,
                file_name=fn3,
                mime="image/jpg",
                use_container_width=True,
            )

        with col2:
            st.download_button(
                label="Download PNG",
                data=img,
                file_name=fn,
                mime="image/png",
                use_container_width=True,
            )


def customDownloadButton2(render1, render2, filename1, filename2):
    if st.button("Download Figures", type="primary", use_container_width=True):
        progress_bar = st.progress(0)

        progress_bar.progress(1 / 2, "Exporting PNGs")
        export_png(render1, filename=filename1 + ".png")
        export_png(render2, filename=filename2 + ".png")

        progress_bar.progress(2 / 2, "Exporting SVGs")
        render1.output_backend = "svg"
        render2.output_backend = "svg"
        export_svgs(render1, filename=filename1 + ".svg")
        export_svgs(render2, filename=filename2 + ".svg")

        progress_bar.empty()

        col1, col2 = st.columns(2)
        with col1:
            with open(filename1 + ".png", "rb") as file:
                st.download_button(
                    label="Download Figure 1 as PNG",
                    data=file,
                    file_name=filename1 + ".png",
                    mime="image/",
                    use_container_width=True,
                    on_click=delete_figures,
                    args=(filename1 + ".svg", filename2 + ".png", filename2 + ".svg"),
                )
            with open(filename1 + ".svg", "rb") as file:
                st.download_button(
                    label="Download Figure 1 as SVG",
                    data=file,
                    file_name=filename1 + ".svg",
                    mime="image/svg",
                    use_container_width=True,
                    on_click=delete_figures,
                    args=(filename1 + ".png", filename2 + ".png", filename2 + ".svg"),
                )

        col3, col4 = st.columns(2)
        with col2:
            with open(filename2 + ".png", "rb") as file:
                st.download_button(
                    label="Download Figure 2 as PNG",
                    data=file,
                    file_name=filename2 + ".png",
                    mime="image/",
                    use_container_width=True,
                    on_click=delete_figures,
                    args=(filename1 + ".png", filename1 + ".svg", filename2 + ".svg"),
                )
            with open(filename2 + ".svg", "rb") as file:
                st.download_button(
                    label="Download Figure 2 as SVG",
                    data=file,
                    file_name=filename2 + ".svg",
                    mime="image/svg",
                    use_container_width=True,
                    on_click=delete_figures,
                    args=(filename1 + ".png", filename1 + ".svg", filename2 + ".png"),
                )
