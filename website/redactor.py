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

def clean_beneficiary_number(text):
    return re.sub(r'\d{3}-\d{4}-\d{4}', '*health plan beneficiary number*', text)

def clean_record_number(text):
    
    return clean_tag(text, 'medical record number')

def clean_certificate(text):

    return clean_tag(text, 'certificate number')

def clean_license(text):

    return clean_tag(text, 'license number')

def clean_serial(text):

    return clean_tag(text, 'pacemaker serial numbers')

def clean_identifier(text):

    return clean_tag(text, 'device identifier')

def clean_url(text):

    return clean_tag(text, 'url')

def clean_code(text):

    text = clean_tag(text, 'code')
    text = clean_tag(text, 'group no.')
    return clean_tag(text, 'health insurance')

def clean_tag(text, tag):
    
    # Find line identified as a tag
    index = re.search(tag + ':', text, re.IGNORECASE)
    if index is None:
        return text

    index = index.start()
    line_index = index + len(tag) + 1
    end = text.find('\n', line_index)

    # Return text without tag
    text = text.replace(text[line_index:end], ' *' + tag + '*')
    newline = text.find('\n', line_index)+1
    return text[:newline] + clean_tag(text[newline:], tag)


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

def clean_address(text):

    # Find line identified as an address
    index = text.find('Address:')
    if index < 0:
        return text
    
    address_line_index = index + 9
    end = text.find('\n', address_line_index)

    # Return input without addresses
    text = text.replace(text[address_line_index:end], ' *address*')
    newline = text.find('\n', address_line_index)+1
    return text[:newline] + clean_address(text[newline:])

def clean_ssn(input):

    # Find line identified as an ssn
    index = input.find('SSN:')
    if index < 0:
        return input
    
    ssn_line_index = index + 5
    end = input.find('\n', ssn_line_index)

    # Return input without ssns
    input = input.replace(input[ssn_line_index:end], ' *SSN*')
    newline = input.find('\n', ssn_line_index)+1
    return input[:newline] + clean_ssn(input[newline:])

def clean_medicaid_acct(input):

    # Medicaid account regex matches nums of form xxxx xxxx xxxx xxxx
    acct_re = r'\d{4} \d{4} \d{4} \d{4}'

    input = re.sub(acct_re, '*medicaid account*', input, flags=re.IGNORECASE)

    # Return input without medicaid accounts
    return input

def clean_allergies(input, allergy_list):
    
    lines = input.split('\n')
    for i in range(len(lines)):
        for allergy in allergy_list:
            match = re.search(allergy, lines[i], flags=re.IGNORECASE)
            if match is not None:
                lines[i] = lines[i][:match.start()] + ' *allergy*'
                break
    input = '\n'.join(lines)

    return input

def clean_results(input):
    
    lines = input.split('\n')
    for i in range(len(lines)):
        match = re.search(r'lab results', lines[i], flags=re.IGNORECASE)
        if match is not None:
            lines[i] = lines[i][:match.start()] + ' *lab results*'
            i += 1
            while True:
                match = re.search(r'- ', lines[i])
                if match is not None:
                    lines[i] = ' - *lab result*'
                    i += 1
                else:
                    break
    input = '\n'.join(lines)

    return input


# --------------------------
# Redaction Filters
# --------------------------

def get_filters(text):
    aliases = {
        'name':                         'name',
        'phone':                        'phone',
        'email':                        'email',
        'date of birth':               'dob',
        'dob':                          'dob',
        'dates':                        'dates',
        'address':                      'address',
        'ssn':                          'ssn',
        'medical record number':       'record_num',
        'medicaid account':            'acct',
        'allergies':                    'allergies',
        'lab results':                 'results',
        'health plan beneficiary number': 'beneficiary_num',
        'certificate number':          'certificate',
        'license number':              'license',
        'pacemaker serial numbers':    'serial',
        'device identifier':           'identifier',
        'url':                          'url',
        'code':                         'code'
    }

    filters = {v: False for v in aliases.values()}
    
    for key, val in aliases.items():
        if re.search(key, text, flags=re.IGNORECASE):
            filters[val] = True
    
    filters['allergy_list'] = []
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
    if filters.get('address'):
        text = clean_address(text)
    if filters.get('ssn'):
        text = clean_ssn(text)
    if filters.get('acct'):
        text = clean_medicaid_acct(text)
    if filters.get('allergies'):
        text = clean_allergies(text, filters['allergy_list'])
    if filters.get('results'):
        text = clean_results(text)
    if filters.get('beneficiary_num'):
        text = clean_beneficiary_number(text)
    if filters.get('record_num'):
        text = clean_record_number(text)
    if filters.get('certificate'):
        text = clean_certificate(text)
    if filters.get('license'):
        text = clean_license(text)
    if filters.get('serial'):
        text = clean_serial(text)
    if filters.get('identifier'):
        text = clean_identifier(text)
    if filters.get('url'):
        text = clean_url(text)
    if filters.get('code'):
        text = clean_code(text)
    return text

# --------------------------
# Flask entrypoint
# --------------------------

def redact_text(text):
    filters = {
        'phone':           True,
        'dates':           True,
        'dob':             True,
        'email':           True,
        'name':            True,
        'address':         True,
        'ssn':             True,
        'acct':            True,
        'allergies':       True,
        'allergy_list':    [],
        'results':         True,
        'beneficiary_num': True,
        'record_num':      True,
        'certificate':     True,
        'license':         True,
        'serial':          True,
        'identifier':      True,
        'url':             True,
        'code':            True
    }
    return clean_text(text, filters)


