def classify_prd(prd_json):
    product_idea = prd_json.get('sections', {}).get('product_idea', '').lower() if prd_json else ''
    
    if 'finance' in product_idea:
        sector = 'Finance'
        category = 'FinTech'
    elif 'health' in product_idea:
        sector = 'Healthcare'
        category = 'HealthTech'
    elif 'education' in product_idea:
        sector = 'Education'
        category = 'EdTech'
    else:
        sector = 'General'
        category = 'Software'
    
    # for req in prd_json.get('sections', {}).get('requirements', []):
    #     req['category'] = category

    return sector, category, prd_json
