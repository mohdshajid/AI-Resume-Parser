import tempfile
from pathlib import Path

import streamlit as st

from Resume_project import (
    parse_job,
    parse_resume,
    read_resume,
    match_candidate,
    rank_candidates
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Resume Screening Dashboard",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📄 Resume Screening Dashboard")

st.write(
    "AI-powered resume screening and candidate ranking "
    "using Groq."
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

st.header("1. Job Description")

job_description = st.text_area(
    "Paste the Job Description",
    height=300,
    placeholder="Paste the complete job description here..."
)


# ============================================================
# RESUME UPLOAD
# ============================================================

st.header("2. Upload Resumes")

uploaded_files = st.file_uploader(
    "Upload candidate resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "🚀 Analyze Candidates",
    type="primary"
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not job_description.strip():

        st.error(
            "Please enter a job description."
        )

        st.stop()


    if not uploaded_files:

        st.error(
            "Please upload at least one resume."
        )

        st.stop()


    # --------------------------------------------------------
    # PARSE JOB
    # --------------------------------------------------------

    with st.spinner("Analyzing job description..."):

        try:

            job = parse_job(
                job_description
            )

        except Exception as e:

            st.error(
                f"Could not analyze job description: {e}"
            )

            st.stop()


    # --------------------------------------------------------
    # SHOW JOB INFORMATION
    # --------------------------------------------------------

    st.success("Job description analyzed successfully.")

    st.subheader("Job Information")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Role**")

        st.write(job.role)

        st.write("**Required Skills**")

        for skill in job.required_skills:

            st.write(f"• {skill}")

    with col2:

        st.write("**Preferred Skills**")

        for skill in job.preferred_skills:

            st.write(f"• {skill}")

        st.write("**Minimum Experience**")

        if job.minimum_experience is not None:

            st.write(
                f"{job.minimum_experience} years"
            )

        else:

            st.write("Not specified")


    # --------------------------------------------------------
    # PROCESS RESUMES
    # --------------------------------------------------------

    st.header("3. Candidate Analysis")

    all_results = []

    progress = st.progress(0)

    total_files = len(uploaded_files)

    for index, uploaded_file in enumerate(uploaded_files):

        st.write(
            f"Processing **{uploaded_file.name}**..."
        )

        try:

            # ------------------------------------------------
            # SAVE TEMPORARY FILE
            # ------------------------------------------------

            suffix = Path(
                uploaded_file.name
            ).suffix

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getvalue()
                )

                temp_path = Path(
                    temp_file.name
                )


            # ------------------------------------------------
            # READ RESUME
            # ------------------------------------------------

            resume_text = read_resume(
                temp_path
            )

            if not resume_text:

                st.warning(
                    f"Could not extract text from "
                    f"{uploaded_file.name}"
                )

                continue


            # ------------------------------------------------
            # PARSE RESUME
            # ------------------------------------------------

            parsed_resume = parse_resume(
                resume_text
            )


            # ------------------------------------------------
            # MATCH CANDIDATE
            # ------------------------------------------------

            result = match_candidate(
                job,
                parsed_resume
            )


            # ------------------------------------------------
            # SAVE RESULT
            # ------------------------------------------------

            all_results.append({

                "file": uploaded_file.name,

                "resume": parsed_resume,

                "match": result

            })


            st.success(
                f"{parsed_resume.name or uploaded_file.name} "
                f"→ {result.score:.1f}%"
            )


        except Exception as e:

            st.error(
                f"Error processing {uploaded_file.name}: {e}"
            )


        finally:

            progress.progress(
                (index + 1) / total_files
            )


    # ========================================================
    # RANK CANDIDATES
    # ========================================================

    if not all_results:

        st.error(
            "No resumes could be processed."
        )

        st.stop()


    all_results = rank_candidates(
        all_results
    )


    # ========================================================
    # RANKING TABLE
    # ========================================================

    st.header("🏆 Candidate Ranking")

    for index, candidate in enumerate(
        all_results,
        start=1
    ):

        resume = candidate["resume"]

        match = candidate["match"]

        candidate_name = (
            resume.name
            or candidate["file"]
        )

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [1, 5, 2]
            )

            with col1:

                st.subheader(
                    f"#{index}"
                )

            with col2:

                st.subheader(
                    candidate_name
                )

                st.caption(
                    candidate["file"]
                )

            with col3:

                st.metric(
                    "Match Score",
                    f"{match.score:.1f}%"
                )


            # ------------------------------------------------
            # DETAILS
            # ------------------------------------------------

            details_col1, details_col2 = st.columns(2)

            with details_col1:

                st.write(
                    "**Matching Skills**"
                )

                if match.matching_skills:

                    for skill in match.matching_skills:

                        st.write(
                            f"✅ {skill}"
                        )

                else:

                    st.write(
                        "No major matching skills found."
                    )


            with details_col2:

                st.write(
                    "**Missing Important Skills**"
                )

                if match.missing_important_skills:

                    for skill in match.missing_important_skills:

                        st.write(
                            f"❌ {skill}"
                        )

                else:

                    st.write(
                        "No major missing skills."
                    )


            st.write(
                "**Experience Requirement:** ",
                "✅ Met"
                if match.experience_requirement_met
                else "❌ Not Met"
            )

            st.write(
                "**Final Verdict:**"
            )

            st.info(
                match.final_verdict
            )


    # ========================================================
    # TOP 2 CANDIDATES
    # ========================================================

    st.header("🥇 Top Candidates")

    top_candidates = all_results[:2]

    columns = st.columns(
        len(top_candidates)
    )

    for column, candidate in zip(
        columns,
        top_candidates
    ):

        resume = candidate["resume"]

        match = candidate["match"]

        with column:

            st.subheader(
                resume.name
                or candidate["file"]
            )

            st.metric(
                "Match",
                f"{match.score:.1f}%"
            )

            st.write(
                match.final_verdict
            )


    # ========================================================
    # HR CANDIDATE SELECTION
    # ========================================================

    st.header("👤 Select Candidate")

    candidate_options = [
        (
            candidate["resume"].name
            or candidate["file"]
        )
        for candidate in all_results
    ]

    selected_candidate = st.selectbox(
        "Choose a candidate to view detailed information",
        candidate_options
    )


    selected_index = candidate_options.index(
        selected_candidate
    )

    selected = all_results[
        selected_index
    ]

    selected_resume = selected["resume"]

    selected_match = selected["match"]


    # ========================================================
    # SELECTED CANDIDATE DETAILS
    # ========================================================

    st.subheader(
        f"Candidate: "
        f"{selected_resume.name or selected['file']}"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write("### Contact")

        st.write(
            f"**Email:** "
            f"{selected_resume.email or 'Not available'}"
        )

        st.write(
            f"**Phone:** "
            f"{selected_resume.phone or 'Not available'}"
        )

        st.write("### Skills")

        for skill in selected_resume.skills:

            st.write(
                f"• {skill}"
            )


    with col2:

        st.write("### Experience")

        if selected_resume.total_experience_years is not None:

            st.write(
                f"**Total Experience:** "
                f"{selected_resume.total_experience_years} years"
            )

        else:

            st.write(
                "**Total Experience:** Not available"
            )


        for experience in selected_resume.experiences:

            st.write(
                f"**{experience.role or 'Role'}** "
                f"at "
                f"**{experience.company or 'Company'}**"
            )

            if experience.duration:

                st.caption(
                    experience.duration
                )


    # ========================================================
    # SELECTED CANDIDATE MATCH
    # ========================================================

    st.subheader("AI Assessment")

    st.metric(
        "Overall Match",
        f"{selected_match.score:.1f}%"
    )

    st.write(
        "**Experience Requirement:**"
    )

    st.write(
        "✅ Met"
        if selected_match.experience_requirement_met
        else "❌ Not Met"
    )

    st.write(
        "**Final Verdict:**"
    )

    st.info(
        selected_match.final_verdict
    )