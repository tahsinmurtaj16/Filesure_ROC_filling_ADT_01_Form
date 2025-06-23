import fitz  # PyMuPDF
import re
import json

pdf_path = "Form ADT-1-29092023_signed.pdf"
doc = fitz.open(pdf_path)

# Extract all text from the PDF
full_text = ""
for page in doc:
    full_text += page.get_text()

lines = full_text.splitlines()

# Extract CIN and Company Name using line-by-line logic
cin_value = ""
company_name = ""
for i, line in enumerate(lines):
    if re.match(r"U[A-Z0-9]{16}", line.strip()):
        cin_value = line.strip()
        if i + 1 < len(lines):
            potential_name = lines[i + 1].strip()
            if "PRIVATE LIMITED" in potential_name or "LIMITED" in potential_name:
                company_name = potential_name
        break

# Helper pattern matcher using regex
def extract_after_pattern(pattern, text, default=""):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return default

# Extract auditor name
auditor_name = extract_after_pattern(r"\n([A-Z &]+)\n001955S", full_text)

# Extract auditor FRN using the auditor name as anchor
auditor_frn_or_membership = ""
if auditor_name:
    pattern = rf"{re.escape(auditor_name)}\s*\n([0-9A-Z]{{6,8}})"
    auditor_frn_or_membership = extract_after_pattern(pattern, full_text)

# Build the final output
extracted_data = {
    "cin": cin_value,
    "company_name": company_name,
    "registered_office": extract_after_pattern(r"(?:PRIVATE LIMITED\n)(.*?),", full_text),
    "appointment_date": extract_after_pattern(r"(?<=From\n)(\d{2}/\d{2}/\d{4})", full_text),
    "auditor_name": auditor_name,
    "auditor_address": extract_after_pattern(r"001955S\n(.*?)\nRace Course Road", full_text) + ", Race Course Road",
    "auditor_frn_or_membership": auditor_frn_or_membership,
    "appointment_type": extract_after_pattern(r"\n1\n(.*?)\nAABFM", full_text),
}

# Save to JSON
output_path = "output.json"
with open(output_path, "w") as f:
    json.dump(extracted_data, f, indent=2)

print("Extracted data saved to:", output_path)
