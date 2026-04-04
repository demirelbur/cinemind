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

    with st.container(border=True):
        st.subheader(f"{index}. {title}")
        st.caption(f"{genre.title()} • {year} • Rating: {rating}/10")

        # col1, col2, col3 = st.columns(3)
        # col1.metric("Director", director)
        # col2.metric("Lead actor", lead_actor)
        # col3.metric(
        #     "Audience",
        #     recommended_for.title()
        #     if isinstance(recommended_for, str)
        #     else recommended_for,
        # )

        st.markdown(
            f"""
        **Director:** {director}
        **Lead actor:** {lead_actor}
        **Audience:** {recommended_for}
        """
        )

        if match_score is not None:
            st.progress(
                max(0.0, min(float(match_score), 1.0)),
                text=f"Match score: {float(match_score):.2f}",
            )

        st.markdown("**Synopsis**")
        st.write(synopsis)

        st.markdown("**Why this matches**")
        st.write(reason)


def main() -> None:
    st.title("🎬 CineMind")
    st.write(
        "Ask for movies in natural language, and CineMind will return grounded recommendations."
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
            if health.get("status") == "ok":
                st.success("Backend is healthy")
            else:
                st.warning("Backend responded unexpectedly")
        except Exception as exc:
            st.error(f"Backend unavailable: {exc}")

    if "history" not in st.session_state:
        st.session_state.history = []

    for entry in st.session_state.history:
        with st.chat_message("user"):
            st.write(entry["query"])
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
            st.write(query)

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
