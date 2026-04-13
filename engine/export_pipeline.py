#!/usr/bin/env python3
"""
PharmaSim Export Pipeline
Generates static JSON files for GitHub Pages frontend
"""
import json
import pathlib
import sys
import sqlite3

# Add parent to path
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from model import score_drug, DIMENSIONS

DB = pathlib.Path(__file__).parent / 'data' / 'pharmasim.db'
EXPORT = pathlib.Path(__file__).parent.parent / 'docs' / 'api'

def get_conn():
    return sqlite3.connect(str(DB))

def export_drugs():
    """Export drug database as JSON."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    drugs = conn.execute('SELECT * FROM drugs ORDER BY therapeutic_area, name').fetchall()
    
    result = []
    for d in drugs:
        drug = dict(d)
        # Get efficacy
        eff = conn.execute('SELECT * FROM clinical_efficacy WHERE drug_id=? ORDER BY sample_size DESC LIMIT 1', (d['id'],)).fetchone()
        drug['efficacy'] = dict(eff) if eff else {}
        
        # Get China status
        cn = conn.execute('SELECT * FROM china_status WHERE drug_id=?', (d['id'],)).fetchone()
        drug['china'] = dict(cn) if cn else {}
        
        # Get pricing
        prices = conn.execute('SELECT * FROM pricing WHERE drug_id=?', (d['id'],)).fetchall()
        drug['pricing'] = {p['market']: {'price_per_month': p['price_per_month'], 'currency': p['currency']} for p in prices}
        
        # Parse JSON fields
        if drug.get('indications_json'):
            drug['indications'] = json.loads(drug['indications_json'])
        
        result.append(drug)
    
    conn.close()
    return result

def export_epidemiology():
    """Export epidemiology data."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM disease_epidemiology').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def export_pipeline():
    """Export pipeline drugs."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM pipeline_drugs').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def export_scores():
    """Score all drugs and export results."""
    conn = get_conn()
    drug_ids = conn.execute('SELECT id, name FROM drugs ORDER BY therapeutic_area, name').fetchall()
    conn.close()
    
    results = []
    for drug_id, name in drug_ids:
        print(f'  Scoring {name}...')
        result = score_drug(drug_id)
        results.append(result)
    
    return results

def export_dimensions():
    """Export dimension definitions."""
    return DIMENSIONS

def run_export():
    """Run full export pipeline."""
    EXPORT.mkdir(parents=True, exist_ok=True)
    
    print('📦 Exporting PharmaSim data...')
    
    # Export drugs
    drugs = export_drugs()
    with open(EXPORT / 'drugs.json', 'w', encoding='utf-8') as f:
        json.dump(drugs, f, ensure_ascii=False, indent=2)
    print(f'  drugs.json: {len(drugs)} drugs')
    
    # Export epidemiology
    epi = export_epidemiology()
    with open(EXPORT / 'epidemiology.json', 'w', encoding='utf-8') as f:
        json.dump(epi, f, ensure_ascii=False, indent=2)
    print(f'  epidemiology.json: {len(epi)} diseases')
    
    # Export pipeline
    pipe = export_pipeline()
    with open(EXPORT / 'pipeline.json', 'w', encoding='utf-8') as f:
        json.dump(pipe, f, ensure_ascii=False, indent=2)
    print(f'  pipeline.json: {len(pipe)} pipeline drugs')
    
    # Export dimensions
    dims = export_dimensions()
    with open(EXPORT / 'dimensions.json', 'w', encoding='utf-8') as f:
        json.dump(dims, f, ensure_ascii=False, indent=2)
    print(f'  dimensions.json: {len(dims)} dimensions')
    
    # Export scores
    scores = export_scores()
    with open(EXPORT / 'scores.json', 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)
    print(f'  scores.json: {len(scores)} scored drugs')
    
    # Export summary
    summary = {
        'version': '3.2',
        'exported_at': scores[0]['timestamp'] if scores else '',
        'total_drugs': len(drugs),
        'total_diseases': len(epi),
        'total_pipeline': len(pipe),
        'dimensions': len(dims),
        'sub_dimensions': sum(len(d['sub_dimensions']) for d in dims.values()),
        'top_drugs': sorted(
            [{'name': s['drug']['name'], 'score': s['composite_score'], 'recommendation': s['recommendation']} 
             for s in scores],
            key=lambda x: x['score'], reverse=True
        )[:5]
    }
    with open(EXPORT / 'summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f'  summary.json: {summary["total_drugs"]} drugs, {summary["sub_dimensions"]} sub-dimensions')
    
    print(f'\n✅ All files exported to {EXPORT}/')
    return summary

if __name__ == '__main__':
    run_export()
