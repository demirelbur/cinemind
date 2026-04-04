import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("CINEMIND_API_BASE_URL", "http://127.0.0.1:8000")
RECOMMEND_ENDPOINT = f"{API_BASE_URL}/recommend"
DEFAULT_MAX_RESULTS = 5
REQUEST_TIMEOUT_SECONDS = 60


st.set_page_config(
    page_title="CineMind",
    page_icon="🎬",
    layout="centered",
)


@st.cache_data(show_spinner=False)
def health_check(api_base_url: str) -> dict[str, Any]:
    response = requests.get(f"{api_base_url}/health", timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_recommendations(query: str, max_results: int | None) -> dict[str, Any]:
    payload: dict[str, Any] = {"query": query}
    if max_results is not None:
        payload["max_results"] = max_results

    response = requests.post(
        RECOMMEND_ENDPOINT,
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --cm-bg: #0b0b0b;
            --cm-bg-soft: #111111;
            --cm-panel: #141414;
            --cm-card: #181818;
            --cm-border: rgba(255,255,255,0.10);
            --cm-text: #f5f5f5;
            --cm-text-soft: #d0d0d0;
            --cm-text-muted: #bdbdbd;
            --cm-accent: #e50914;
            --cm-accent-soft: #ff5f6d;
        }

        html, body {
            background: var(--cm-bg) !important;
            color: var(--cm-text) !important;
        }

        .stApp {
            background:
                radial-gradient(circle at top, rgba(229,9,20,0.10) 0%, rgba(229,9,20,0.02) 18%, rgba(0,0,0,0.0) 36%),
                linear-gradient(180deg, #0b0b0b 0%, #111111 45%, #0b0b0b 100%) !important;
            color: var(--cm-text) !important;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top, rgba(229,9,20,0.10) 0%, rgba(229,9,20,0.02) 18%, rgba(0,0,0,0.0) 36%),
                linear-gradient(180deg, #0b0b0b 0%, #111111 45%, #0b0b0b 100%) !important;
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }

        .main .block-container {
            background: transparent !important;
            max-width: 900px;
            padding-top: 2rem;
            padding-bottom: 8rem;
        }

        section[data-testid="stSidebar"] {
            background: #0d0d0d !important;
            border-right: 1px solid var(--cm-border);
        }

        section[data-testid="stSidebar"] * {
            color: var(--cm-text) !important;
        }

        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #ffffff !important;
        }

        .stApp p, .stApp label, .stApp li, .stApp span, .stApp div {
            color: var(--cm-text-soft);
        }

        div[data-testid="stMarkdownContainer"] p {
            color: var(--cm-text-soft) !important;
        }

        [data-testid="stCaptionContainer"] {
            color: #c9c9c9 !important;
        }

        div[data-testid="stChatMessage"] {
            background: transparent !important;
            border: none !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        div[data-testid="stChatMessageContent"] {
            background: transparent !important;
            color: var(--cm-text) !important;
        }

        /* --- critical: bottom portal / chat area --- */
        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"] {
            background: transparent !important;
        }

        [data-testid="stBottom"] > div,
        [data-testid="stBottomBlockContainer"] > div {
            background: transparent !important;
        }

        [data-testid="stChatInputContainer"],
        [data-testid="stChatInput"] {
            background: transparent !important;
        }

        [data-testid="stChatInputContainer"] > div,
        [data-testid="stChatInput"] > div {
            background: var(--cm-panel) !important;
            border: 1px solid var(--cm-border) !important;
            border-radius: 18px !important;
            box-shadow: 0 12px 30px rgba(0,0,0,0.35) !important;
        }

        [data-testid="stChatInputContainer"] > div > div,
        [data-testid="stChatInput"] > div > div {
            background: var(--cm-panel) !important;
            border-radius: 18px !important;
        }

        [data-testid="stChatInput"] form,
        [data-testid="stChatInputContainer"] form {
            background: transparent !important;
        }

        [data-testid="stChatInputTextArea"] {
            background: transparent !important;
        }

        [data-testid="stChatInputTextArea"] > div {
            background: transparent !important;
        }

        [data-testid="stChatInput"] [data-baseweb="textarea"],
        [data-testid="stChatInput"] [data-baseweb="base-input"],
        [data-testid="stChatInput"] [role="textbox"] {
            background: transparent !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }

        [data-testid="stChatInputTextArea"] div[contenteditable="true"] {
            background: transparent !important;
            color: var(--cm-text) !important;
            -webkit-text-fill-color: var(--cm-text) !important;
            caret-color: #ffffff !important;
        }

        [data-testid="stChatInput"] textarea {
            background: transparent !important;
            color: var(--cm-text) !important;
            -webkit-text-fill-color: var(--cm-text) !important;
            caret-color: #ffffff !important;
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: var(--cm-text-muted) !important;
            opacity: 1 !important;
            -webkit-text-fill-color: var(--cm-text-muted) !important;
        }

        /* Some Streamlit versions render an inner input-like element */
        [data-testid="stChatInput"] input {
            background: transparent !important;
            color: var(--cm-text) !important;
            -webkit-text-fill-color: var(--cm-text) !important;
            caret-color: #ffffff !important;
        }

        [data-testid="stChatInput"] input::placeholder {
            color: var(--cm-text-muted) !important;
            opacity: 1 !important;
            -webkit-text-fill-color: var(--cm-text-muted) !important;
        }

        /* Ensure message bubbles never fall back to a light container */
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
        [data-testid="stChatMessage"] [data-testid="stVerticalBlock"],
        [data-testid="stChatMessage"] [data-testid="stHorizontalBlock"] {
            background: transparent !important;
        }

        [data-testid="stChatInputSubmitButton"] button {
            background: linear-gradient(135deg, #ff4b4b 0%, #e50914 100%) !important;
            color: #ffffff !important;
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.16) !important;
            opacity: 1 !important;
            box-shadow: 0 8px 20px rgba(229,9,20,0.35) !important;
        }

        [data-testid="stChatInputSubmitButton"],
        [data-testid="stChatInputSubmitButton"] > div {
            opacity: 1 !important;
            filter: none !important;
        }

        [data-testid="stChatInputSubmitButton"] button:hover {
            background: linear-gradient(135deg, #ff6a6a 0%, #ff2b2b 100%) !important;
        }

        [data-testid="stChatInputSubmitButton"] button svg,
        [data-testid="stChatInputSubmitButton"] button path {
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }

        [data-testid="stChatInputSubmitButton"] button:disabled {
            background: linear-gradient(135deg, #ff8a92 0%, #ff6f79 100%) !important;
            color: #fff5f6 !important;
            border: 1px solid rgba(255,255,255,0.20) !important;
            box-shadow: 0 6px 14px rgba(255,111,121,0.20) !important;
            opacity: 1 !important;
        }

        [data-testid="stChatInputSubmitButton"] button[disabled],
        [data-testid="stChatInputSubmitButton"] button[aria-disabled="true"] {
            background: linear-gradient(135deg, #ff8a92 0%, #ff6f79 100%) !important;
            color: #fff5f6 !important;
            border: 1px solid rgba(255,255,255,0.20) !important;
            box-shadow: 0 6px 14px rgba(255,111,121,0.20) !important;
            opacity: 1 !important;
            filter: none !important;
        }

        [data-testid="stChatInputSubmitButton"]:has(button[disabled]),
        [data-testid="stChatInputSubmitButton"]:has(button[aria-disabled="true"]) {
            opacity: 1 !important;
            filter: none !important;
        }

        button[data-baseweb="tab"] {
            color: #d7d7d7 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #ffffff !important;
        }

        [data-testid="stAlertContainer"] {
            border-radius: 12px;
        }

        .cinemind-subtitle {
            color: var(--cm-text-soft) !important;
            font-size: 1.05rem;
            margin-bottom: 1.25rem;
        }

        .cinemind-user-query {
            color: var(--cm-text) !important;
            font-size: 1.05rem;
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_movie_card(item: dict[str, Any], index: int) -> None:
    movie = item.get("movie", {})
    reason = item.get("reason", "")
    match_score = item.get("match_score")

    title = movie.get("title", "Unknown title")
    genre = movie.get("genre", "-")
    year = movie.get("year", "-")
    rating = movie.get("rating", "-")
    synopsis = movie.get("synopsis", "No synopsis available.")
    director = movie.get("director") or "Unknown"
    lead_actor = movie.get("lead_actor") or "Unknown"
    recommended_for = movie.get("recommended_for") or "Not specified"

    score_pct = 0
    score_label = "N/A"
    if match_score is not None:
        score_pct = max(0, min(int(float(match_score) * 100), 100))
        score_label = f"{float(match_score):.2f}"

    audience_text = (
        recommended_for.title() if isinstance(recommended_for, str) else recommended_for
    )
    genre_text = genre.title() if isinstance(genre, str) else genre

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(180deg, #181818 0%, #121212 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 1.2rem 1.2rem 1rem 1.2rem;
            margin: 0.8rem 0 1rem 0;
            box-shadow: 0 10px 24px rgba(0,0,0,0.22);
        ">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; flex-wrap:wrap;">
                <div>
                    <div style="font-size:0.82rem; color:#b3b3b3; margin-bottom:0.35rem;">Recommendation #{index}</div>
                    <div style="font-size:1.7rem; font-weight:700; color:#ffffff; line-height:1.2;">{title}</div>
                    <div style="margin-top:0.45rem; color:#cfcfcf; font-size:0.98rem;">
                        <span style="background:#e50914; color:white; padding:0.18rem 0.48rem; border-radius:999px; font-size:0.78rem; font-weight:700; margin-right:0.45rem;">{genre_text}</span>
                        <span>{year}</span>
                        <span style="margin:0 0.45rem;">•</span>
                        <span>⭐ {rating}/10</span>
                    </div>
                </div>
                <div style="min-width:170px; max-width:220px; flex:1;">
                    <div style="font-size:0.8rem; color:#b3b3b3; margin-bottom:0.35rem;">Match score</div>
                    <div style="font-size:1.05rem; color:#ffffff; font-weight:600; margin-bottom:0.4rem;">{score_label}</div>
                    <div style="width:100%; height:8px; background:#2a2a2a; border-radius:999px; overflow:hidden;">
                        <div style="width:{score_pct}%; height:100%; background:linear-gradient(90deg, #e50914 0%, #ff5f6d 100%);"></div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        st.markdown("**Director**")
        st.caption(director)
    with meta_col2:
        st.markdown("**Lead actor**")
        st.caption(lead_actor)
    with meta_col3:
        st.markdown("**Audience**")
        st.caption(audience_text)

    tab1, tab2 = st.tabs(["Synopsis", "Why it matches"])
    with tab1:
        st.write(synopsis)
    with tab2:
        st.write(reason)


def main() -> None:
    apply_global_styles()

    st.markdown("<h1>🎬 CineMind</h1>", unsafe_allow_html=True)
    st.markdown(
        '<div class="cinemind-subtitle">Ask for movies in natural language, and CineMind will return grounded recommendations.</div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Settings")
        use_custom_max = st.toggle("Set recommendation count manually", value=False)
        max_results = None
        if use_custom_max:
            max_results = st.slider(
                "Number of recommendations",
                min_value=1,
                max_value=10,
                value=DEFAULT_MAX_RESULTS,
            )

        st.divider()
        st.caption(f"API: {API_BASE_URL}")

        try:
            health = health_check(API_BASE_URL)
            status_value = str(health.get("status", "")).lower()
            if status_value in {"ok", "healthy", "success"}:
                st.success("Backend is healthy")
            else:
                st.warning(f"Backend check returned: {health}")
        except Exception as exc:
            st.error(f"Backend unavailable: {exc}")

    if "history" not in st.session_state:
        st.session_state.history = []

    for entry in st.session_state.history:
        with st.chat_message("user"):
            st.markdown(
                f'<div class="cinemind-user-query">{entry["query"]}</div>',
                unsafe_allow_html=True,
            )
        with st.chat_message("assistant"):
            recommendations = entry.get("recommendations", [])
            if not recommendations:
                st.info("No recommendations returned.")
            for idx, item in enumerate(recommendations, start=1):
                render_movie_card(item, idx)

    query = st.chat_input(
        "Example: Recommend 3 dark sci-fi movies from the 80s for teens"
    )

    if query:
        with st.chat_message("user"):
            st.markdown(
                f'<div class="cinemind-user-query">{query}</div>',
                unsafe_allow_html=True,
            )

        with st.chat_message("assistant"):
            with st.spinner("Finding movies..."):
                try:
                    response = fetch_recommendations(
                        query=query, max_results=max_results
                    )
                except requests.HTTPError as exc:
                    detail = None
                    try:
                        detail = exc.response.json().get("detail")
                    except Exception:
                        detail = (
                            exc.response.text if exc.response is not None else str(exc)
                        )
                    st.error(f"Recommendation request failed: {detail}")
                    return
                except requests.RequestException as exc:
                    st.error(f"Could not reach the backend: {exc}")
                    return

            recommendations = response.get("recommendations", [])
            if not recommendations:
                st.info("No recommendations found. Try broadening your query.")
            else:
                for idx, item in enumerate(recommendations, start=1):
                    render_movie_card(item, idx)

            st.session_state.history.append(
                {
                    "query": query,
                    "recommendations": recommendations,
                }
            )


if __name__ == "__main__":
    main()
