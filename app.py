import re
import fitz  # PyMuPDF
import spacy
import time
import pandas as pd
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Skill keywords (kept unchanged)
skill_keywords = [
    "Python", "Java", "JavaScript", "C++", "SQL", "MongoDB", "PostgreSQL", "Machine Learning",
    "Deep Learning", "Neural Networks", "Data Science", "AI", "Django", "Flask", "React", "React Native", "Node.js",
    "TensorFlow", "PyTorch", "API", "AWS", "Cloud Computing", "DevOps", "Competitive Programming","Data Structures",
    "Algorithms", "Web Development", "Software Development", "Computer Vision", "Natural Language Processing","Data Science",
    "Data Analysis", "Business Intelligence", "Power BI", "Tableau", "Big Data", "Hadoop", "Spark", "ETL", "CI/CD","Kubernetes",
    "Docker", "Git", "Linux", "Unix", "Shell Scripting", "Automation", "Agile", "Scrum", "Kanban", "Problem Solving","HTML",
    "CSS", "Bootstrap", "SASS", "LESS", "jQuery", "Angular", "Vue.js", "TypeScript", "Svelte", "Web Design", "UI/UX","REST",
    "GraphQL", "Microservices", "Serverless", "Blockchain", "Cryptocurrency", "Solidity", "Ethereum", "DeFi", "NFT","Cybersecurity",
    "Ethical Hacking", "Penetration Testing", "OWASP", "Firewall", "VPN", "Security Audits", "Compliance", "ISO 27001","Risk Management",
    "Fraud Detection", "Identity & Access Management", "SIEM", "Splunk", "Networking", "TCP/IP", "DNS", "HTTP", "SSL","Wireless Networks",
    "Network Security", "Firewall", "Cisco", "Juniper", "CompTIA", "CCNA", "CCNP", "CCIE", "CEH", "CISSP", "CISM","CISA",
]

exclude_list = ["EBTS Organization", "AuxPlutes Tech"]

def extract_skills(about_text):
    """Extracts skills from the About section using keyword matching & NLP"""
    extracted_skills = []
    lower_text = about_text.lower()

    for skill in skill_keywords:
        if skill.lower() in lower_text:
            extracted_skills.append(skill)

    doc = nlp(about_text)
    for token in doc.ents:
        if token.label_ in ["ORG", "PRODUCT"]:
            extracted_skills.append(token.text)

    return list(set(extracted_skills))

def extract_linkedin_from_resume(pdf_path):
    """Extracts LinkedIn URL from a resume PDF"""
    linkedin_pattern = r"https?://(?:www\.)?linkedin\.com/[A-Za-z0-9-_/]+"
    doc = fitz.open(pdf_path)

    for page_num in range(min(3, len(doc))):
        text = doc[page_num].get_text("text")
        linkedin_urls = re.findall(linkedin_pattern, text)
        if linkedin_urls:
            return linkedin_urls[0]
    return "No LinkedIn URL found"

def login_linkedin(driver, email, password):
    """Logs into LinkedIn with user-provided credentials"""
    driver.get("https://www.linkedin.com/login")
    time.sleep(3)
    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password + Keys.RETURN)
    time.sleep(20)  # Allow manual CAPTCHA completion

def scrape_linkedin_profile(linkedin_url, email, password):
    """Scrapes LinkedIn profile for Name and About section (same as your working version)"""
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    login_linkedin(driver, email, password)
    driver.get(linkedin_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    name_section = soup.find("h1")
    name = name_section.text.strip() if name_section else "No Name Found"

    about_section = soup.find("div", {"class": "display-flex ph5 pv3"})
    about_text = about_section.text.strip() if about_section else "No About section found"

    return {
        "name": name,
        "about": about_text,
        "linkedin_url": linkedin_url
    }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        file = request.files.get("pdf")

        if file and email and password:
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            file_path = os.path.join("uploads", file.filename)
            file.save(file_path)

            linkedin_url = extract_linkedin_from_resume(file_path)

            if "linkedin.com" in linkedin_url:
                profile_data = scrape_linkedin_profile(linkedin_url, email, password)
                skills_identified = extract_skills(profile_data["about"])
                profile_data["skills"] = ", ".join([skill for skill in skills_identified if skill not in exclude_list])
                return render_template("result.html", profile=profile_data)
            else:
                return render_template("index.html", error="No LinkedIn URL found in the resume.")
    
    return render_template("index.html")
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)