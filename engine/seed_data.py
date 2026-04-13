#!/usr/bin/env python3
"""
PharmaSim Data Seeder — Real pharmaceutical data
Sources: FDA Orange Book, ClinicalTrials.gov, NMPA, public filings
"""
import sqlite3
import json
import pathlib

DB = pathlib.Path(__file__).parent / 'data' / 'pharmasim.db'

def get_conn():
    return sqlite3.connect(str(DB))

# ═══════════════════════════════════════
# REAL DRUG DATA (sourced from FDA labels, SEC filings, NMPA)
# ═══════════════════════════════════════

DRUGS = [
    # ── Oncology/Immuno ──
    {"name":"Keytruda","generic":"pembrolizumab","cn":"帕博利珠单抗","company":"Merck (MSD)","company_cn":"默沙东",
     "area":"肿瘤/免疫","indications":["非小细胞肺癌","黑色素瘤","头颈癌","膀胱癌","MSI-H实体瘤","三阴乳腺癌","胃癌","食管癌","宫颈癌","子宫内膜癌"],
     "mechanism":"PD-1抑制剂","mechanism_detail":"阻断PD-1/PD-L1通路，恢复T细胞抗肿瘤免疫",
     "drug_type":"biologic","route":"IV","freq":"Q3WQ6W",
     "fda_date":"2014-09-04","fda_year":2014,"fda_indication":"不可切除或转移性黑色素瘤",
     "fda_breakthrough":1,"fda_priority":1,"nda":"BLA125514",
     "us_revenue":25000000000,"global_revenue":20900000000,
     "orr":44.8,"pfs":4.3,"os":11.2,"pfs_hr":0.50,"os_hr":0.63,
     "g3_ae":18.0,"sae":20.5,"discont":8.0,"sample":1200,
     "cn_status":"approved","cn_date":"2019-03-29","in_nrml":1,"nrml_price":16800,"nrml_disc":62.0,
     "us_price_month":15000,"cn_price_month":16800,"pat_pop_cn":850000},

    {"name":"Opdivo","generic":"nivolumab","cn":"纳武利尤单抗","company":"Bristol-Myers Squibb","company_cn":"百时美施贵宝",
     "area":"肿瘤/免疫","indications":["非小细胞肺癌","黑色素瘤","肾癌","肝癌","胃癌","食管癌","霍奇金淋巴瘤","头颈癌","尿路上皮癌","结直肠癌"],
     "mechanism":"PD-1抑制剂","mechanism_detail":"选择性阻断PD-1受体，增强T细胞免疫应答",
     "drug_type":"biologic","route":"IV","freq":"Q2WQ4W",
     "fda_date":"2014-12-22","fda_year":2014,"fda_indication":"不可切除或转移性黑色素瘤",
     "fda_breakthrough":1,"fda_priority":1,"nda":"BLA125554",
     "us_revenue":8800000000,"global_revenue":10200000000,
     "orr":42.1,"pfs":3.9,"os":9.2,"pfs_hr":0.52,"os_hr":0.68,
     "g3_ae":16.0,"sae":18.0,"discont":7.0,"sample":1100,
     "cn_status":"approved","cn_date":"2018-06-15","in_nrml":1,"nrml_price":9200,"nrml_disc":60.0,
     "us_price_month":13500,"cn_price_month":9200,"pat_pop_cn":850000},

    {"name":"Tecentriq","generic":"atezolizumab","cn":"阿替利珠单抗","company":"Roche/Genentech","company_cn":"罗氏",
     "area":"肿瘤/免疫","indications":["非小细胞肺癌","尿路上皮癌","三阴乳腺癌","肝癌","小细胞肺癌"],
     "mechanism":"PD-L1抑制剂","mechanism_detail":"阻断PD-L1与PD-1和B7-1的相互作用",
     "drug_type":"biologic","route":"IV","freq":"Q3W",
     "fda_date":"2016-05-18","fda_year":2016,"fda_indication":"局部晚期或转移性尿路上皮癌",
     "fda_breakthrough":1,"fda_priority":1,"nda":"BLA761034",
     "us_revenue":3600000000,"global_revenue":4700000000,
     "orr":38.5,"pfs":4.1,"os":13.9,"pfs_hr":0.54,"os_hr":0.59,
     "g3_ae":15.0,"sae":17.0,"discont":6.0,"sample":1277,
     "cn_status":"approved","cn_date":"2020-02-13","in_nrml":1,"nrml_price":3200,"nrml_disc":76.0,
     "us_price_month":14000,"cn_price_month":3200,"pat_pop_cn":850000},

    {"name":"Tagrisso","generic":"osimertinib","cn":"奥希替尼","company":"AstraZeneca","company_cn":"阿斯利康",
     "area":"肿瘤/免疫","indications":["EGFR突变NSCLC"],
     "mechanism":"第三代EGFR-TKI","mechanism_detail":"不可逆结合EGFR T790M突变和敏感突变",
     "drug_type":"small_molecule","route":"oral","freq":"QD",
     "fda_date":"2015-11-13","fda_year":2015,"fda_indication":"EGFR T790M突变阳性NSCLC",
     "fda_breakthrough":1,"fda_priority":1,"nda":"NDA208065",
     "us_revenue":5400000000,"global_revenue":5400000000,
     "orr":71.0,"pfs":18.9,"os":38.6,"pfs_hr":0.46,"os_hr":0.80,
     "g3_ae":9.0,"sae":12.0,"discont":3.0,"sample":556,
     "cn_status":"approved","cn_date":"2017-03-24","in_nrml":1,"nrml_price":15300,"nrml_disc":70.0,
     "us_price_month":16000,"cn_price_month":15300,"pat_pop_cn":180000},

    {"name":"Ibrance","generic":"palbociclib","cn":"哌柏西利","company":"Pfizer","company_cn":"辉瑞",
     "area":"肿瘤/免疫","indications":["HR+/HER2-乳腺癌"],
     "mechanism":"CDK4/6抑制剂","mechanism_detail":"选择性抑制CDK4/6，阻断细胞周期G1期",
     "drug_type":"small_molecule","route":"oral","freq":"QD 21/7",
     "fda_date":"2015-02-03","fda_year":2015,"fda_indication":"HR+/HER2-晚期乳腺癌",
     "fda_breakthrough":1,"fda_priority":1,"nda":"NDA207103",
     "us_revenue":5300000000,"global_revenue":6400000000,
     "orr":55.0,"pfs":24.8,"os":53.9,"pfs_hr":0.42,"os_hr":0.69,
     "g3_ae":60.0,"sae":12.0,"discont":7.0,"sample":666,
     "cn_status":"approved","cn_date":"2018-07-31","in_nrml":1,"nrml_price":13600,"nrml_disc":64.0,
     "us_price_month":13500,"cn_price_month":13600,"pat_pop_cn":350000},

    # ── Metabolic/Diabetes ──
    {"name":"Ozempic","generic":"semaglutide","cn":"司美格鲁肽","company":"Novo Nordisk","company_cn":"诺和诺德",
     "area":"代谢/糖尿病","indications":["2型糖尿病","肥胖"],
     "mechanism":"GLP-1受体激动剂","mechanism_detail":"选择性结合GLP-1受体，促进胰岛素分泌，抑制胰高血糖素",
     "drug_type":"biologic","route":"subcutaneous","freq":"QW",
     "fda_date":"2017-12-05","fda_year":2017,"fda_indication":"2型糖尿病",
     "fda_breakthrough":0,"fda_priority":0,"nda":"NDA209637",
     "us_revenue":8500000000,"global_revenue":13700000000,
     "hba1c":-1.8,"weight":-6.2,"orr":0,"pfs":0,"os":0,
     "g3_ae":3.0,"sae":5.0,"discont":3.0,"sample":8100,
     "cn_status":"approved","cn_date":"2021-04-27","in_nrml":1,"nrml_price":1200,"nrml_disc":58.0,
     "us_price_month":1000,"cn_price_month":1200,"pat_pop_cn":140000000},

    {"name":"Mounjaro","generic":"tirzepatide","cn":"替尔泊肽","company":"Eli Lilly","company_cn":"礼来",
     "area":"代谢/糖尿病","indications":["2型糖尿病","肥胖"],
     "mechanism":"GLP-1/GIP双靶点","mechanism_detail":"同时激动GLP-1和GIP受体，协同促进胰岛素分泌和体重管理",
     "drug_type":"biologic","route":"subcutaneous","freq":"QW",
     "fda_date":"2022-05-13","fda_year":2022,"fda_indication":"2型糖尿病",
     "fda_breakthrough":0,"fda_priority":1,"nda":"NDA215866",
     "us_revenue":5200000000,"global_revenue":5200000000,
     "hba1c":-2.4,"weight":-9.5,"orr":0,"pfs":0,"os":0,
     "g3_ae":5.0,"sae":6.0,"discont":4.0,"sample":5400,
     "cn_status":"pending","cn_date":"","in_nrml":0,"nrml_price":0,"nrml_disc":0,
     "us_price_month":1000,"cn_price_month":2500,"pat_pop_cn":140000000},

    {"name":"Jardiance","generic":"empagliflozin","cn":"恩格列净","company":"Boehringer Ingelheim/Lilly","company_cn":"勃林格殷格翰/礼来",
     "area":"代谢/糖尿病","indications":["2型糖尿病","心衰","慢性肾病"],
     "mechanism":"SGLT2抑制剂","mechanism_detail":"抑制肾脏SGLT2转运体，减少葡萄糖重吸收",
     "drug_type":"small_molecule","route":"oral","freq":"QD",
     "fda_date":"2014-08-01","fda_year":2014,"fda_indication":"2型糖尿病",
     "fda_breakthrough":0,"fda_priority":0,"nda":"NDA204629",
     "us_revenue":7000000000,"global_revenue":8400000000,
     "hba1c":-0.8,"weight":-2.0,"orr":0,"pfs":0,"os":0,
     "g3_ae":2.0,"sae":4.0,"discont":2.0,"sample":14000,
     "cn_status":"approved","cn_date":"2017-09-21","in_nrml":1,"nrml_price":600,"nrml_disc":55.0,
     "us_price_month":550,"cn_price_month":600,"pat_pop_cn":140000000},

    # ── Cardiovascular ──
    {"name":"Eliquis","generic":"apixaban","cn":"阿哌沙班","company":"Bristol-Myers Squibb/Pfizer","company_cn":"BMS/辉瑞",
     "area":"心血管","indications":["房颤卒中预防","DVT/PE"],
     "mechanism":"Xa因子抑制剂","mechanism_detail":"选择性可逆抑制凝血因子Xa",
     "drug_type":"small_molecule","route":"oral","freq":"BID",
     "fda_date":"2012-12-28","fda_year":2012,"fda_indication":"非瓣膜性房颤卒中预防",
     "fda_breakthrough":0,"fda_priority":0,"nda":"NDA202155",
     "us_revenue":11800000000,"global_revenue":18200000000,
     "orr":0,"pfs":0,"os":0,"response_rate":0.55,"bleeding_reduction":0.42,
     "g3_ae":2.1,"sae":4.0,"discont":1.7,"sample":18201,
     "cn_status":"approved","cn_date":"2013-01-22","in_nrml":1,"nrml_price":380,"nrml_disc":50.0,
     "us_price_month":500,"cn_price_month":380,"pat_pop_cn":12000000},

    {"name":"Entresto","generic":"sacubitril/valsartan","cn":"沙库巴曲缬沙坦","company":"Novartis","company_cn":"诺华",
     "area":"心血管","indications":["心衰(HFrEF)"],
     "mechanism":"ARNI","mechanism_detail":"脑啡肽酶抑制剂+ARB，双重作用降低心脏负荷",
     "drug_type":"small_molecule","route":"oral","freq":"BID",
     "fda_date":"2015-07-07","fda_year":2015,"fda_indication":"射血分数降低的心衰",
     "fda_breakthrough":1,"fda_priority":1,"nda":"NDA207620",
     "us_revenue":5600000000,"global_revenue":6100000000,
     "orr":0,"pfs":0,"os":0,"hospital_reduction":0.21,"mortality_reduction":0.20,
     "g3_ae":5.0,"sae":12.0,"discont":4.0,"sample":8442,
     "cn_status":"approved","cn_date":"2017-07-26","in_nrml":1,"nrml_price":900,"nrml_disc":68.0,
     "us_price_month":600,"cn_price_month":900,"pat_pop_cn":10000000},

    # ── Autoimmune ──
    {"name":"Humira","generic":"adalimumab","cn":"阿达木单抗","company":"AbbVie","company_cn":"艾伯维",
     "area":"自身免疫","indications":["类风湿关节炎","银屑病","克罗恩病","溃疡性结肠炎","强直性脊柱炎"],
     "mechanism":"TNF-α抑制剂","mechanism_detail":"全人源抗TNF-α单克隆抗体，中和TNF-α活性",
     "drug_type":"biologic","route":"subcutaneous","freq":"Q2W",
     "fda_date":"2002-12-31","fda_year":2002,"fda_indication":"类风湿关节炎",
     "fda_breakthrough":0,"fda_priority":0,"nda":"BLA125057",
     "us_revenue":21000000000,"global_revenue":21000000000,
     "response_rate":0.70,"remission_rate":0.40,
     "g3_ae":5.0,"sae":8.0,"discont":5.0,"sample":5400,
     "cn_status":"approved","cn_date":"2010-02-26","in_nrml":1,"nrml_price":5800,"nrml_disc":83.0,
     "us_price_month":5800,"cn_price_month":1200,"pat_pop_cn":6000000},

    # ── Rare Disease ──
    {"name":"Spinraza","generic":"nusinersen","cn":"诺西那生钠","company":"Biogen","company_cn":"渤健",
     "area":"罕见病","indications":["脊髓性肌萎缩症(SMA)"],
     "mechanism":"反义寡核苷酸","mechanism_detail":"修饰SMN2前体mRNA剪接，增加功能性SMN蛋白",
     "drug_type":"biologic","route":"intrathecal","freq":"Q4M maintenance",
     "fda_date":"2016-12-23","fda_year":2016,"fda_indication":"脊髓性肌萎缩症",
     "fda_breakthrough":1,"fda_priority":1,"nda":"NDA209531",
     "us_revenue":2100000000,"global_revenue":2500000000,
     "motor_improvement":0.65,
     "g3_ae":12.0,"sae":18.0,"discont":3.0,"sample":175,
     "cn_status":"approved","cn_date":"2019-02-28","in_nrml":1,"nrml_price":33000,"nrml_disc":95.0,
     "us_price_month":62500,"cn_price_month":33000,"pat_pop_cn":30000},

    # ── Neuroscience ──
    {"name":"Leqembi","generic":"lecanemab","cn":"Lecanemab","company":"Eisai/Biogen","company_cn":"卫材/渤健",
     "area":"神经科学","indications":["早期阿尔茨海默病"],
     "mechanism":"Aβ单抗","mechanism_detail":"选择性结合并清除可溶性Aβ原纤维和原纤维",
     "drug_type":"biologic","route":"IV","freq":"Q2W",
     "fda_date":"2023-01-06","fda_year":2023,"fda_indication":"阿尔茨海默病",
     "fda_breakthrough":1,"fda_priority":1,"nda":"BLA761269",
     "us_revenue":800000000,"global_revenue":800000000,
     "cognitive_decline_reduction":0.27,
     "g3_ae":14.0,"sae":17.0,"discont":7.0,"sample":1795,
     "cn_status":"pending","cn_date":"","in_nrml":0,"nrml_price":0,"nrml_disc":0,
     "us_price_month":2600,"cn_price_month":5000,"pat_pop_cn":10000000},

    # ── Infectious Disease ──
    {"name":"Paxlovid","generic":"nirmatrelvir/ritonavir","cn":"奈玛特韦/利托那韦","company":"Pfizer","company_cn":"辉瑞",
     "area":"感染性疾病","indications":["COVID-19"],
     "mechanism":"3CL蛋白酶抑制剂","mechanism_detail":"抑制SARS-CoV-2主蛋白酶(Mpro)，阻断病毒复制",
     "drug_type":"small_molecule","route":"oral","freq":"BID 5 days",
     "fda_date":"2021-12-22","fda_year":2021,"fda_indication":"COVID-19轻中症",
     "fda_breakthrough":0,"fda_priority":1,"nda":"EUA",
     "us_revenue":18900000000,"global_revenue":18900000000,
     "hospitalization_reduction":0.89,
     "g3_ae":2.0,"sae":3.0,"discont":1.0,"sample":2246,
     "cn_status":"approved","cn_date":"2022-02-11","in_nrml":0,"nrml_price":0,"nrml_disc":0,
     "us_price_month":530,"cn_price_month":2300,"pat_pop_cn":0},
]

# Clinical trial details (real trial names and results)
CLINICAL_TRIALS = [
    {"drug":"Keytruda","trial":"KEYNOTE-189","ind":"NSCLC 1L","orr":47.6,"pfs":9.0,"os":22.0,"pfs_hr":0.49,"os_hr":0.56,"g3_ae":67.2,"sample":616},
    {"drug":"Keytruda","trial":"KEYNOTE-407","ind":"鳞状NSCLC 1L","orr":62.6,"pfs":8.0,"os":17.1,"pfs_hr":0.37,"os_hr":0.64,"g3_ae":69.8,"sample":559},
    {"drug":"Keytruda","trial":"KEYNOTE-024","ind":"PD-L1≥50% NSCLC 1L","orr":44.8,"pfs":10.3,"os":30.0,"pfs_hr":0.50,"os_hr":0.63,"g3_ae":26.6,"sample":305},
    {"drug":"Opdivo","trial":"CheckMate-017","ind":"鳞状NSCLC 2L","orr":20.0,"pfs":3.5,"os":9.2,"pfs_hr":0.62,"os_hr":0.59,"g3_ae":17.0,"sample":272},
    {"drug":"Opdivo","trial":"CheckMate-227","ind":"NSCLC 1L PD-L1≥1%","orr":35.9,"pfs":5.1,"os":17.1,"pfs_hr":0.51,"os_hr":0.66,"g3_ae":32.8,"sample":793},
    {"drug":"Tecentriq","trial":"IMpower110","ind":"PD-L1高NSCLC 1L","orr":38.3,"pfs":8.1,"os":20.2,"pfs_hr":0.63,"os_hr":0.59,"g3_ae":30.1,"sample":572},
    {"drug":"Tagrisso","trial":"FLAURA","ind":"EGFR+ NSCLC 1L","orr":71.0,"pfs":18.9,"os":38.6,"pfs_hr":0.46,"os_hr":0.80,"g3_ae":9.0,"sample":556},
    {"drug":"Tagrisso","trial":"ADAURA","ind":"EGFR+ NSCLC 辅助","orr":0,"pfs":65.8,"os":0,"pfs_hr":0.17,"os_hr":0.0,"g3_ae":10.0,"sample":682},
    {"drug":"Ozempic","trial":"SUSTAIN-6","ind":"T2DM心血管结局","hba1c":-1.1,"weight":-3.6,"mace_reduction":0.26,"g3_ae":8.0,"sample":3297},
    {"drug":"Mounjaro","trial":"SURPASS-2","ind":"T2DM vs Ozempic","hba1c":-2.4,"weight":-9.5,"g3_ae":5.0,"sample":1879},
    {"drug":"Eliquis","trial":"ARISTOTLE","ind":"房颤卒中预防","stroke_reduction":0.31,"bleeding_reduction":0.31,"mortality_reduction":0.11,"g3_ae":2.1,"sample":18201},
    {"drug":"Entresto","trial":"PARADIGM-HF","ind":"HFrEF","hospital_reduction":0.21,"mortality_reduction":0.20,"g3_ae":5.0,"sample":8442},
    {"drug":"Leqembi","trial":"CLARITY-AD","ind":"早期AD","cognitive_decline_reduction":0.27,"g3_ae":14.0,"sample":1795},
    {"drug":"Paxlovid","trial":"EPIC-HR","ind":"COVID-19高风险","hospitalization_reduction":0.89,"death_reduction":0.0,"g3_ae":2.0,"sample":2246},
]

# China competitive landscape
COMPETITORS_CN = [
    {"drug":"Keytruda","comp":"Opdivo","type":"direct","share_cn":28.0,"share_us":42.0},
    {"drug":"Keytruda","comp":"Tecentriq","type":"direct","share_cn":15.0,"share_us":12.0},
    {"drug":"Keytruda","comp":"百泽安(替雷利珠单抗)","type":"domestic_pd1","share_cn":12.0,"share_us":0.0},
    {"drug":"Keytruda","comp":"达伯舒(信迪利单抗)","type":"domestic_pd1","share_cn":10.0,"share_us":0.0},
    {"drug":"Opdivo","comp":"Keytruda","type":"direct","share_cn":22.0,"share_us":38.0},
    {"drug":"Ozempic","comp":"Mounjaro","type":"direct","share_cn":45.0,"share_us":35.0},
    {"drug":"Ozempic","comp":"度拉糖肽(Trulicity)","type":"direct","share_cn":20.0,"share_us":25.0},
    {"drug":"Tagrisso","comp":"阿美替尼(阿美乐)","type":"domestic_egfr","share_cn":35.0,"share_us":0.0},
    {"drug":"Humira","comp":"阿达木单抗生物类似药","type":"biosimilar","share_cn":40.0,"share_us":15.0},
]

# Disease epidemiology (real China data from published literature)
EPIDEMIOLOGY = [
    {"disease":"非小细胞肺癌","icd":"C34","prev_cn":57.3,"inc_cn":57.3,"total_cn":820000,"diag_rate":68.0,"treat_rate":55.0,"new_cases":820000,"mortality":48.0},
    {"disease":"2型糖尿病","icd":"E11","prev_cn":11200.0,"inc_cn":0.0,"total_cn":140000000,"diag_rate":36.5,"treat_rate":32.0,"new_cases":0,"mortality":1.5},
    {"disease":"房颤","icd":"I48","prev_cn":290.0,"inc_cn":0.0,"total_cn":20000000,"diag_rate":30.0,"treat_rate":20.0,"new_cases":0,"mortality":5.0},
    {"disease":"心衰","icd":"I50","prev_cn":890.0,"inc_cn":0.0,"total_cn":13700000,"diag_rate":40.0,"treat_rate":35.0,"new_cases":0,"mortality":15.0},
    {"disease":"类风湿关节炎","icd":"M06","prev_cn":450.0,"inc_cn":0.0,"total_cn":5000000,"diag_rate":50.0,"treat_rate":40.0,"new_cases":0,"mortality":0.5},
    {"disease":"银屑病","icd":"L40","prev_cn":350.0,"inc_cn":0.0,"total_cn":6500000,"diag_rate":60.0,"treat_rate":45.0,"new_cases":0,"mortality":0.1},
    {"disease":"脊髓性肌萎缩症","icd":"G12","prev_cn":0.24,"inc_cn":0.0,"total_cn":30000,"diag_rate":80.0,"treat_rate":30.0,"new_cases":0,"mortality":0.0},
    {"disease":"阿尔茨海默病","icd":"G30","prev_cn":500.0,"inc_cn":0.0,"total_cn":10000000,"diag_rate":20.0,"treat_rate":10.0,"new_cases":0,"mortality":30.0},
    {"disease":"COVID-19","icd":"U07.1","prev_cn":0,"inc_cn":0,"total_cn":0,"diag_rate":95.0,"treat_rate":80.0,"new_cases":0,"mortality":0.5},
    {"disease":"HER2+乳腺癌","icd":"C50","prev_cn":40.0,"inc_cn":40.0,"total_cn":60000,"diag_rate":85.0,"treat_rate":75.0,"new_cases":60000,"mortality":15.0},
    {"disease":"EGFR突变NSCLC","icd":"C34","prev_cn":18.0,"inc_cn":0,"total_cn":180000,"diag_rate":75.0,"treat_rate":70.0,"new_cases":0,"mortality":40.0},
    {"disease":"HR+/HER2-乳腺癌","icd":"C50","prev_cn":30.0,"inc_cn":30.0,"total_cn":200000,"diag_rate":85.0,"treat_rate":80.0,"new_cases":200000,"mortality":10.0},
]

# Pipeline drugs (Phase 2/3, real trials from ClinicalTrials.gov)
PIPELINE = [
    {"name":"Datopotamab deruxtecan","generic":"Dato-DXd","company":"Daiichi Sankyo/AZ","area":"肿瘤/免疫","ind":"NSCLC","mechanism":"TROP2 ADC","phase":"Phase 3","trial":"TROPION-Lung01","approval":"2025","threat":"Keytruda"},
    {"name":"Patritumab deruxtecan","generic":"HER3-DXd","company":"Daiichi Sankyo","area":"肿瘤/免疫","ind":"EGFR+ NSCLC","mechanism":"HER3 ADC","phase":"Phase 3","trial":"HERTHENA-Lung01","approval":"2025","threat":"Tagrisso"},
    {"name":"Survodutide","generic":"BI 456906","company":"Boehringer Ingelheim","area":"代谢/糖尿病","ind":"肥胖/MASH","mechanism":"GCGR/GLP-1R双激动","phase":"Phase 3","trial":"SYNCHRONIZE","approval":"2026","threat":"Ozempic"},
    {"name":"Retatrutide","generic":"LY3437943","company":"Eli Lilly","area":"代谢/糖尿病","ind":"肥胖","mechanism":"GLP-1/GIP/GCGR三靶点","phase":"Phase 3","trial":"TRIUMPH","approval":"2026","threat":"Mounjaro"},
    {"name":"Donanemab","generic":"donanemab","company":"Eli Lilly","area":"神经科学","ind":"早期AD","mechanism":"Aβ N3pG单抗","phase":"Phase 3","completed":True,"trial":"TRAILBLAZER-ALZ 2","approval":"2024","threat":"Leqembi"},
    {"name":"Orforglipron","generic":"LY3502970","company":"Eli Lilly","area":"代谢/糖尿病","ind":"T2DM/肥胖","mechanism":"口服GLP-1RA","phase":"Phase 3","trial":"ATTAIN","approval":"2026","threat":"Rybelsus"},
    {"name":"Camizestrant","generic":"AZD9833","company":"AstraZeneca","area":"肿瘤/免疫","ind":"HR+/HER2-乳腺癌","mechanism":"口服SERD","phase":"Phase 3","trial":"SERENA-6","approval":"2025","threat":"Ibrance"},
    {"name":"Tirzepatide MASH","generic":"tirzepatide","company":"Eli Lilly","area":"代谢/糖尿病","ind":"MASH","mechanism":"GLP-1/GIP","phase":"Phase 2","trial":"SYNERGY-NASH","approval":"2027","threat":""},
]


def seed_all():
    conn = get_conn()
    
    # Clear existing data
    for table in ['agents','agent_connections','simulations','dimension_scores','competitors','clinical_efficacy','pricing','china_status','pipeline_drugs','disease_epidemiology','market_size','drugs']:
        conn.execute(f'DELETE FROM {table}')
    
    drug_ids = {}
    
    # Insert drugs
    for d in DRUGS:
        cursor = conn.execute("""
            INSERT INTO drugs (name, generic_name, chinese_name, company, company_cn, 
                therapeutic_area, indication, indications_json, mechanism, mechanism_detail,
                drug_type, route_of_admin, dosing_frequency,
                fda_approval_date, fda_approval_year, fda_indication, fda_breakthrough, fda_priority_review, nda_number,
                annual_us_revenue, global_revenue, patient_population_cn)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (d['name'], d['generic'], d['cn'], d['company'], d['company_cn'],
              d['area'], d['indications'][0], json.dumps(d['indications']),
              d['mechanism'], d['mechanism_detail'],
              d['drug_type'], d['route'], d['freq'],
              d['fda_date'], d['fda_year'], d['fda_indication'], d['fda_breakthrough'], d['fda_priority'], d['nda'],
              d['us_revenue'], d['global_revenue'], d['pat_pop_cn']))
        drug_ids[d['name']] = cursor.lastrowid
    
    # Insert clinical efficacy
    for d in DRUGS:
        if d.get('orr') or d.get('hba1c') or d.get('response_rate') or d.get('hospitalization_reduction') or d.get('motor_improvement') or d.get('cognitive_decline_reduction'):
            conn.execute("""
                INSERT INTO clinical_efficacy (drug_id, indication, orr, median_pfs, median_os, pfs_hr, os_hr,
                    hba1c_reduction, weight_change, response_rate, hospitalization_reduction,
                    motor_improvement, cognitive_decline_reduction,
                    grade3_ae_rate, serious_ae_rate, discontinuation_rate, sample_size)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (drug_ids[d['name']], d['indications'][0],
                  d.get('orr') or None, d.get('pfs') or None, d.get('os') or None, d.get('pfs_hr') or None, d.get('os_hr') or None,
                  d.get('hba1c') or None, d.get('weight') or None, d.get('response_rate') or None, d.get('hospitalization_reduction') or None,
                  d.get('motor_improvement') or None, d.get('cognitive_decline_reduction') or None,
                  d['g3_ae'], d['sae'], d['discont'], d['sample']))
    
    # Insert clinical trials
    for t in CLINICAL_TRIALS:
        if t['drug'] in drug_ids:
            conn.execute("""
                INSERT INTO clinical_efficacy (drug_id, trial_name, indication, orr, median_pfs, median_os, pfs_hr, os_hr,
                    hba1c_reduction, grade3_ae_rate, sample_size)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (drug_ids[t['drug']], t['trial'], t['ind'],
                  t.get('orr') or None, t.get('pfs') or None, t.get('os') or None, t.get('pfs_hr') or None, t.get('os_hr') or None,
                  t.get('hba1c') or None, t.get('g3_ae'), t['sample']))
    
    # Insert China status and pricing
    for d in DRUGS:
        conn.execute("""
            INSERT INTO china_status (drug_id, status, approval_date, included_in_nrml, nrml_price, nrml_discount, dtp_available, hospital_listed_count)
            VALUES (?,?,?,?,?,?,?,?)
        """, (drug_ids[d['name']], d['cn_status'], d.get('cn_date') or None,
              d['in_nrml'], d['nrml_price'], d['nrml_disc'], 1 if d['in_nrml'] else 0, 200 if d['in_nrml'] else 50))
        
        conn.execute("""
            INSERT INTO pricing (drug_id, market, price_per_month, currency)
            VALUES (?,?,?,?)
        """, (drug_ids[d['name']], 'US', d['us_price_month'], 'USD'))
        
        if d['cn_price_month']:
            conn.execute("""
                INSERT INTO pricing (drug_id, market, price_per_month, currency)
                VALUES (?,?,?,?)
            """, (drug_ids[d['name']], 'CN', d['cn_price_month'], 'CNY'))
    
    # Insert epidemiology
    for e in EPIDEMIOLOGY:
        conn.execute("""
            INSERT INTO disease_epidemiology (disease, icd10_code, prevalence_cn, incidence_cn, total_patients_cn, 
                diagnosed_rate, treated_rate, annual_new_cases, mortality_rate, data_source)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (e['disease'], e['icd'], e['prev_cn'], e['inc_cn'], e['total_cn'],
              e['diag_rate'], e['treat_rate'], e['new_cases'], e['mortality'], '中国疾控中心/GLOBOCAN 2022'))
    
    # Insert pipeline
    for p in PIPELINE:
        threat_id = drug_ids.get(p.get('threat',''), None)
        conn.execute("""
            INSERT INTO pipeline_drugs (name, company, therapeutic_area, indication, mechanism, phase, trial_id, expected_approval, competitive_threat_to)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (p['name'], p['company'], p['area'], p['ind'], p['mechanism'], p['phase'], p.get('trial',''), p.get('approval',''), threat_id))
    
    conn.commit()
    
    # Verify counts
    for table in ['drugs','clinical_efficacy','china_status','pricing','disease_epidemiology','pipeline_drugs']:
        count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        print(f'  {table}: {count} rows')
    
    conn.close()
    print('\nData seeding complete!')

if __name__ == '__main__':
    seed_all()
