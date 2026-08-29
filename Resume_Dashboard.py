import os
import time
from pathlib import Path
# from services.job_parser import parse_job
from dotenv import load_dotenv
from groq import Groq

# from services.job_parser import parse_job
# from services.resume_parser import parse_resume
# from services.matcher import match_candidate
# from services.ranking import rank_candidates

# from utils.file_reader import read_resume


# -----------------------------------
# ENVIRONMENT
# -----------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found")


client = Groq(api_key=api_key)


# -----------------------------------
# JOB DESCRIPTION
# -----------------------------------

job_description = """
Description

Do you want to solve real customer problems through innovative technology?
Do you enjoy working on scalable services in a collaborative team environment?
Do you want to see your code directly impact millions of customers worldwide?

At Amazon, we hire the best minds in technology to innovate and build on behalf
of our customers.

Our Software Development Engineers (SDEs) use modern technology to solve
complex problems while seeing their work's impact first-hand.

We're looking for curious minds who think big and want to define tomorrow's
technology.

As an SDE-I, you'll own the entire lifecycle of your code - from design
through deployment and ongoing operations.
"""


# -----------------------------------
# PARSE JOB
# -----------------------------------

print("\nAnalyzing job description...")

job = parse_job(
    client,
    job_description
)

print("\nJOB INFORMATION")

print("Role:", job.role)

print("Required Skills:")
for skill in job.required_skills:
    print("-", skill)

print("Preferred Skills:")
for skill in job.preferred_skills:
    print("-", skill)

print(
    "Minimum Experience:",
    job.minimum_experience
)


# -----------------------------------
# PROCESS RESUMES
# -----------------------------------

resume_folder = Path("resumes")

all_results = []


for file_path in resume_folder.iterdir():

    if file_path.suffix.lower() not in [".pdf", ".docx"]:
        continue

    print("\n--------------------------------")
    print("Processing:", file_path.name)
    print("--------------------------------")

    try:

        # ----------------------------
        # Read resume
        # ----------------------------

        resume_text = read_resume(file_path)

        if not resume_text.strip():

            print("Could not extract text.")
            continue


        # ----------------------------
        # Parse resume
        # ----------------------------

        print("Parsing resume...")

        parsed_resume = parse_resume(
            client,
            resume_text
        )


        # ----------------------------
        # Rate-limit protection
        # ----------------------------

        time.sleep(5)


        # ----------------------------
        # Match candidate
        # ----------------------------

        print("Matching candidate...")

        result = match_candidate(
            client,
            job,
            parsed_resume
        )


        # ----------------------------
        # Save result
        # ----------------------------

        all_results.append({

            "file": file_path.name,

            "resume": parsed_resume,

            "match": result

        })


        print(
            "Candidate:",
            parsed_resume.name
        )

        print(
            "Score:",
            result.score
        )


        time.sleep(5)


    except Exception as e:

        print(
            f"Error processing {file_path.name}: {e}"
        )


# -----------------------------------
# RANK CANDIDATES
# -----------------------------------

all_results = rank_candidates(
    all_results
)


# -----------------------------------
# TOP 2
# -----------------------------------

top_2 = all_results[:2]


print("\n\n================================")
print("TOP 2 CANDIDATES")
print("================================")


for index, candidate in enumerate(top_2, start=1):

    resume = candidate["resume"]
    match = candidate["match"]

    print(
        f"\n{index}. {resume.name}"
    )

    print(
        "Score:",
        match.score
    )

    print(
        "Matching Skills:",
        ", ".join(match.matching_skills)
    )

    print(
        "Missing Skills:",
        ", ".join(
            match.missing_important_skills
        )
    )

    print(
        "Experience Requirement Met:",
        match.experience_requirement_met
    )

    print(
        "Verdict:",
        match.final_verdict
    )