# -*- coding: utf-8 -*-
"""
Master resume content for Sriram Akula.
Sourced directly from the resume he provided (Sriram_Akula_Crompton.pdf) -
this is the base the CV generator selects, reorders, and rephrases from.
It never invents a skill, project, or line of experience to chase a
higher ATS score.
"""

CONTACT = {
    "name": "Sriram Akula",
    "email": "sriramakula29@gmail.com",
    "phone": "+91 9381715664",
    "linkedin": "linkedin.com/in/sriram-akula-771580269",
    "github": "github.com/sriram-akula",
    "portfolio": "akula-data-canvas.lovable.app",
    "location": "Bangalore, India (Open to Relocate)",
}

SUMMARY_BASE = (
    "M.Sc. Analytics candidate at Tata Institute of Social Sciences (TISS), Mumbai and B.Tech "
    "Computer Science Engineering graduate with hands-on experience in Product Analytics, Data "
    "Operations, Business Intelligence, Dashboard Development, and Reporting Automation. Skilled "
    "in SQL, Python, Advanced Excel, Power BI, SAP, and SQL Server for data extraction, validation, "
    "transformation, and visualization. Experienced in working with large structured datasets, "
    "maintaining data quality, executing analytical workflows, automating repetitive reporting "
    "tasks, and delivering actionable insights through dashboards and reports. Strong attention to "
    "detail, analytical thinking, problem-solving ability, process improvement mindset, and "
    "enthusiasm for AI-assisted automation and product operations."
)

SKILLS = {
    "Programming": {
        "Python": ["python"],
        "SQL": ["sql", "t-sql", "pl/sql"],
        "PySpark": ["pyspark", "spark"],
    },
    "Data Operations": {
        "Data Extraction": ["data extraction", "extraction"],
        "Data Cleaning": ["data cleaning", "cleansing"],
        "Data Validation": ["data validation", "validation"],
        "Data Transformation": ["data transformation", "transformation", "etl"],
        "Data Quality Management": ["data quality"],
    },
    "Analytics": {
        "Business Analytics": ["business analytics", "business analysis"],
        "Statistical Analysis": ["statistical analysis", "statistics", "hypothesis testing"],
        "Product Analysis": ["product analytics", "product analysis"],
        "Trend Analysis": ["trend analysis"],
        "Exploratory Data Analysis": ["eda", "exploratory data analysis"],
        "Machine Learning": ["machine learning", "predictive modeling", "predictive analytics", "scikit-learn", "sklearn"],
    },
    "Reporting & BI": {
        "Power BI": ["power bi", "powerbi"],
        "Dashboard Development": ["dashboard", "dashboards"],
        "Advanced Excel": ["excel", "advanced excel", "vlookup", "pivot table"],
        "Power Query": ["power query"],
        "MIS Reporting": ["mis reporting", "mis"],
        "KPI Reporting": ["kpi", "kpi reporting", "kpi analysis"],
    },
    "Enterprise Tools": {
        "SAP": ["sap"],
        "SQL Server": ["sql server"],
        "Semantic Models": ["semantic model", "semantic models"],
        "Power BI Service": ["power bi service"],
    },
    "Automation": {
        "Power BI REST API": ["power bi rest api", "rest api"],
        "Workflow Automation": ["workflow automation", "automation"],
        "Reporting Automation": ["reporting automation"],
        "AI-assisted Reporting": ["ai-assisted", "genai", "generative ai", "llm", "prompt engineering"],
    },
    "Cloud Computing": {
        "AWS S3": ["s3", "aws s3"],
        "AWS Athena": ["athena", "aws athena"],
        "Redshift": ["redshift"],
        "QuickSight": ["quicksight"],
    },
}

EDUCATION = [
    {
        "degree": "M.Sc. Analytics",
        "school": "Tata Institute of Social Sciences (TISS), Mumbai",
        "years": "2025 - 2026",
        "detail": "CGPA 7.8",
    },
    {
        "degree": "B.Tech, Computer Science Engineering",
        "school": "JNTU Kakinada",
        "years": "2021 - 2025",
        "detail": "CGPA 8.22",
    },
    {
        "degree": "Class XII",
        "school": "Sasi Junior College, Velivennu",
        "years": "2019 - 2021",
        "detail": "97.9%",
    },
    {
        "degree": "Class X",
        "school": "Sasi School, Nidadavole",
        "years": "2018 - 2019",
        "detail": "98%",
    },
]

EXPERIENCE = [
    {
        "title": "Data Analyst Intern",
        "org": "Crompton Greaves Consumer Electricals Ltd.",
        "dates": "Apr 2026 - Jun 2026",
        "bullets": [
            "Extracted enterprise data from SAP and executed structured data preparation, transformation, and validation workflows for analytical reporting and business intelligence solutions.",
            "Developed semantic models using SQL Server to organize enterprise datasets and enable efficient analytical querying.",
            "Wrote optimized SQL queries to extract business insights, perform KPI analysis, and support reporting requirements across multiple business functions.",
            "Designed, published, and maintained interactive dashboards using Power BI Service while ensuring data quality, reporting consistency, and adherence to organizational reporting standards.",
            "Collaborated with business stakeholders to understand reporting requirements, troubleshoot data issues, and deliver scalable analytical solutions supporting operational and strategic decision-making.",
        ],
        "tags": ["sap", "sql server", "semantic model", "power bi service", "kpi", "data validation", "data transformation", "dashboard", "stakeholder"],
    },
    {
        "title": "Business Analyst Intern",
        "org": "Raymond Pvt Ltd",
        "dates": "Dec 2025 - Jan 2026",
        "bullets": [
            "Collected, cleaned, validated, transformed, and analyzed over 100K+ retail transaction records using SQL, Advanced Excel, and Power BI to support business intelligence and product analytics initiatives.",
            "Performed structured data validation, quality checks, KPI analysis, and trend analysis to ensure reporting accuracy and consistency across business reports.",
            "Developed interactive Power BI dashboards, KPI scorecards, and automated reporting solutions that enabled stakeholders to monitor customer behavior, sales performance, and operational metrics.",
            "Collaborated with business teams to gather reporting requirements, document analytical outputs, identify process improvement opportunities, and deliver actionable insights supporting data-driven decision-making and operational excellence.",
        ],
        "tags": ["sql", "excel", "power bi", "kpi", "trend analysis", "data validation", "retail", "product analytics", "dashboard", "stakeholder"],
    },
]

PROJECTS = [
    {
        "name": "Customer Shift Analysis & Customer Analytics Dashboard",
        "detail": (
            "Analyzed over 100K+ customer transactions using SQL, Excel, and Power BI to identify customer "
            "migration patterns, retention behavior, revenue leakage, and business growth opportunities across "
            "multiple retail formats. Built interactive dashboards, transition matrices, and customer analytics "
            "reports to visualize retention rates, customer journeys, and business performance."
        ),
        "tags": ["sql", "excel", "power bi", "dashboard", "customer analytics", "segmentation", "kpi", "retail"],
    },
    {
        "name": "Automated MIS Reporting & Dashboard Automation",
        "detail": (
            "Developed an automated reporting framework using Python, Power Query, Power BI REST API, and Excel "
            "to streamline recurring reporting workflows and dashboard refresh processes across 10K+ business "
            "records, cutting manual reporting effort by 60% and improving turnaround time by 50%."
        ),
        "tags": ["python", "power query", "power bi rest api", "excel", "automation", "mis", "reporting automation"],
    },
    {
        "name": "Customer Churn Prediction & Predictive Analytics",
        "detail": (
            "Developed a predictive analytics solution using Python, SQL, Pandas, NumPy, and Scikit-learn on "
            "over 50K+ customer records to identify at-risk customers, uncover churn drivers, and support "
            "retention strategy through interactive dashboards communicating findings to stakeholders."
        ),
        "tags": ["python", "sql", "machine learning", "scikit-learn", "predictive modeling", "eda", "feature engineering", "dashboard"],
    },
]

CERTIFICATIONS = [
    "AI Readiness & Mindset Report 2026 - Published with Whitespaces Consultancy (2026)",
    "Lean Six Sigma Green Belt - Grant Thornton India (2025)",
    "Cloud Computing - NPTEL, IIT Kharagpur (2023)",
]

ACHIEVEMENTS = []

TARGET_ROLE_LABELS = ["Data Analyst", "Data Scientist", "BI Analyst", "SQL Developer"]
