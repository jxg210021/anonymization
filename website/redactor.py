import re

# --------------------------
# Individual cleaning functions
# --------------------------

def clean_phone(text):
    return re.sub(r'\d{3}-\d{3}-\d{4}', '*phone*', text)

def clean_date(text):
    return re.sub(r'\b(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/(19|20)\d\d\b', '*date*', text)

def clean_dob(text):
    pattern = r'(dob|date of birth): (0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/(19|20)\d\d'
    return re.sub(pattern, r'\1: *dob*', text, flags=re.IGNORECASE)

def clean_email(text):
    return re.sub(r'\b[a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', '*email*', text)

def clean_names(text):
    lines = text.split('\n')
    name_keywords = ['patient:', 'provider:', 'patient name:', 'provider name:', 'hospital name:', 'social worker:']
    name_remove = ['patient:', 'patient name:']
    found_names = []

    for i in range(len(lines)):
        for tag in name_keywords:
            if re.search(tag, lines[i], flags=re.IGNORECASE):
                if tag in name_remove:
                    found_names.extend(lines[i].split()[1:])
                lines[i] = tag + ' *name*'
                break

    text = '\n'.join(lines)
    for name in found_names:
        text = re.sub(r'\b{}\b'.format(re.escape(name)), '*name*', text)
    
    honorifics = [r'\bmr\.?', r'\bmrs\.?', r'\bdr\.?', r'\bms\.?', r'\bmiss\b']
    for h in honorifics:
        text = re.sub(h, '', text, flags=re.IGNORECASE)

    return text

# --------------------------
# Redaction Filters
# --------------------------

def get_filters(text):
    aliases = {
        'name': 'name',
        'phone': 'phone',
        'email': 'email',
        'date of birth': 'dob',
        'dob': 'dob',
        'dates': 'dates'
    }

    filters = {v: False for v in aliases.values()}
    
    for key, val in aliases.items():
        if re.search(key, text, flags=re.IGNORECASE):
            filters[val] = True

    return filters

def clean_text(text, filters):
    if filters.get('phone'):
        text = clean_phone(text)
    if filters.get('dates'):
        text = clean_date(text)
    if filters.get('dob'):
        text = clean_dob(text)
    if filters.get('email'):
        text = clean_email(text)
    if filters.get('name'):
        text = clean_names(text)
    return text

# --------------------------
# Flask entrypoint
# --------------------------

def redact_text(text):
    filters = {
        'phone': True,
        'dates': True,
        'dob': True,
        'email': True,
        'name': True
    }
    return clean_text(text, filters)


