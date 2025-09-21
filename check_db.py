from database import DatabaseManager

db = DatabaseManager()

print("=== JOB DESCRIPTIONS ===")
jds = db.get_job_descriptions()
print(f"Count: {len(jds)}")
for jd in jds:
    print(f"ID: {jd['id']}, Company: {jd['company']}, Role: {jd['role']}")

print("\n=== RESUMES ===")
resumes = db.get_resumes()
print(f"Count: {len(resumes)}")
for r in resumes:
    print(f"ID: {r['id']}, Name: {r['candidate_name']}, Email: {r['email']}")

print("\n=== ANALYSIS RESULTS ===")
results = db.get_analysis_results()
print(f"Count: {len(results)}")
for r in results:
    print(f"Resume ID: {r['resume_id']}, JD ID: {r['job_description_id']}, Score: {r['relevance_score']}")