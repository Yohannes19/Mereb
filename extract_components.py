import re

with open(r'd:\Project\rateMe\templates\dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract Navbar
navbar_match = re.search(r'(<!-- Professional Navbar -->.*?</nav>)', content, re.DOTALL)
if navbar_match:
    with open(r'd:\Project\rateMe\templates\components\navbar.html', 'w', encoding='utf-8') as f:
        f.write(navbar_match.group(1))

# Extract Sidebar
sidebar_match = re.search(r'(<div class="col-md-4 col-lg-3 col-xl-2 sidebar-container">.*?</div>\s*</div>\s*</div>)', content, re.DOTALL)
if sidebar_match:
    with open(r'd:\Project\rateMe\templates\components\sidebar.html', 'w', encoding='utf-8') as f:
        f.write(sidebar_match.group(1))

# Split tabs out of the main content
# Using `re.split` or replace.
# It is better to write totally new files for tabs based on IDs:
tab_profile = re.search(r'(<div class="tab-pane fade [^"]*"[^>]*id="pills-profile"[^>]*>.*?</div>\s*</div>\s*</div>)', content, re.DOTALL)
if tab_profile:
    with open(r'd:\Project\rateMe\templates\components\tab_profile.html', 'w', encoding='utf-8') as f:
        f.write(tab_profile.group(1))

tab_proof = re.search(r'(<!-- Proof Tab -->\s*<div class="tab-pane fade [^"]*"[^>]*id="pills-proof"[^>]*>.*?</div>\s*</div>\s*</div>)', content, re.DOTALL)
if tab_proof:
    with open(r'd:\Project\rateMe\templates\components\tab_proof.html', 'w', encoding='utf-8') as f:
        f.write(tab_proof.group(1))

tab_rating = re.search(r'(<!-- Rating Form Tab -->\s*<div class="tab-pane fade [^"]*"[^>]*id="pills-rating"[^>]*>.*?</div>\s*</div>\s*</div>)', content, re.DOTALL)
if tab_rating:
    with open(r'd:\Project\rateMe\templates\components\tab_rating.html', 'w', encoding='utf-8') as f:
        f.write(tab_rating.group(1))

tab_feed = re.search(r'(<!-- Activity Feed Tab -->\s*<div class="tab-pane fade"[^>]*id="pills-feed"[^>]*>.*?</div>\s*</div>\s*</div>)', content, re.DOTALL)
if tab_feed:
    with open(r'd:\Project\rateMe\templates\components\tab_feed.html', 'w', encoding='utf-8') as f:
        f.write(tab_feed.group(1))

print("Component extraction script complete.")
