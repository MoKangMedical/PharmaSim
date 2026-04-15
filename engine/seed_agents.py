#!/usr/bin/env python3
"""
PharmaSim Agent Profile Generator
生成1801个完整profile的Agent数据，包含卡通头像
数据导出为JSON供前端使用
"""

import sqlite3
import random
import json
import hashlib
import os

# ═══════════════════════════════════════
# 中国城市数据
# ═══════════════════════════════════════
CITIES_TIER1 = ['北京', '上海', '广州', '深圳', '成都', '杭州', '武汉', '南京', '重庆', '天津']
CITIES_TIER2 = ['苏州', '西安', '郑州', '长沙', '东莞', '青岛', '沈阳', '宁波', '昆明', '大连',
                '厦门', '合肥', '佛山', '福州', '哈尔滨', '济南', '温州', '南宁', '长春', '石家庄']
CITIES_TIER3 = ['贵阳', '南昌', '金华', '常州', '嘉兴', '徐州', '太原', '珠海', '惠州', '保定',
                '台州', '中山', '绍兴', '扬州', '兰州', '烟台', '廊坊', '泉州', '唐山', '芜湖']

HOSPITALS = {
    1: ['北京协和医院', '北京大学第一医院', '复旦大学附属中山医院', '上海交通大学医学院附属瑞金医院',
        '四川大学华西医院', '华中科技大学同济医学院附属同济医院', '浙江大学医学院附属第一医院',
        '中山大学附属第一医院', '中国医学科学院肿瘤医院', '北京大学人民医院'],
    2: ['江苏省人民医院', '武汉大学人民医院', '山东省立医院', '郑州大学第一附属医院',
        '中南大学湘雅医院', '天津医科大学总医院', '重庆医科大学附属第一医院',
        '哈尔滨医科大学附属第一医院', '西安交通大学第一附属医院', '福建省立医院']
}

SPECIALTIES = {
    '肿瘤科': ['肺癌', '胃癌', '乳腺癌', '结直肠癌', '肝癌', '淋巴瘤'],
    '心内科': ['冠心病', '心力衰竭', '高血压', '心律失常'],
    '内分泌科': ['糖尿病', '甲状腺疾病', '骨质疏松'],
    '神经内科': ['阿尔茨海默病', '帕金森病', '癫痫', '多发性硬化'],
    '风湿免疫科': ['类风湿关节炎', '系统性红斑狼疮', '强直性脊柱炎'],
    '消化内科': ['炎症性肠病', '肝硬化', '胃食管反流病'],
    '呼吸科': ['慢性阻塞性肺病', '哮喘', '肺纤维化']
}

EXPERT_DIMS = {
    'epidemiology': {'cn': '流行病学', 'focus': ['疾病负担', '流行趋势', '风险因素', '筛查策略']},
    'clinical': {'cn': '临床评估', 'focus': ['临床试验设计', '疗效评价', '安全性监测', '真实世界研究']},
    'market': {'cn': '市场分析', 'focus': ['市场准入', '竞争格局', '渠道策略', '商业模型']},
    'pricing': {'cn': '定价策略', 'focus': ['价值定价', '国际比价', '支付意愿', '价格弹性']},
    'pharmacology': {'cn': '药物学', 'focus': ['药理机制', '药代动力学', '药物相互作用', '制剂技术']},
    'pharmaecon': {'cn': '药物经济学', 'focus': ['成本效果分析', '预算影响分析', 'QALY评价', 'ICER阈值']},
    'insurance': {'cn': '医保政策', 'focus': ['基金测算', '目录调整', '谈判策略', '支付改革']}
}

UNIVERSITIES = ['北京大学公共卫生学院', '复旦大学公共卫生学院', '北京协和医学院', '上海交通大学医学院',
                '浙江大学医学院', '四川大学华西医学院', '中国药科大学', '北京大学药学院',
                '北京大学光华管理学院', '清华大学经济管理学院', '中国人民大学经济学院',
                '北京大学国家发展研究院', '清华大学公共管理学院', '北京大学政府管理学院']

LAST_NAMES = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
              '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧', '程', '曹', '袁', '邓', '许']
FIRST_MALE = ['伟', '强', '磊', '洋', '勇', '军', '杰', '涛', '超', '明', '刚', '平', '辉', '鑫', '波', '斌', '宇', '浩', '凯', '健']
FIRST_FEMALE = ['芳', '娜', '敏', '静', '丽', '霞', '秀', '玲', '艳', '素云', '莲', '真', '雪', '爱', '慧', '琳', '颖', '婷', '燕', '洁']

DISEASES = ['肺癌', '胃癌', '乳腺癌', '结直肠癌', '肝癌', '淋巴瘤', '白血病', '糖尿病', '高血压', '冠心病',
            '心力衰竭', '类风湿关节炎', '系统性红斑狼疮', '阿尔茨海默病', '帕金森病', '慢性阻塞性肺病',
            '哮喘', '炎症性肠病', '癫痫', '多发性硬化']

TITLES = ['教授', '副教授', '研究员', '副研究员', '院士', '长江学者', '杰青']
TREATMENT_HX = ['初诊', '一线治疗中', '二线治疗中', '三线治疗中', '多线治疗失败', '维持治疗中']
ATTITUDES_DOCTOR = ['积极推荐', '支持使用', '谨慎推荐', '观望态度', '持保留意见']
ATTITUDES_PATIENT = ['积极治疗', '保守治疗', '观望中', '寻求替代', '犹豫不决']
ATTITUDES_EXPERT = ['支持创新', '严谨审慎', '数据驱动', '平衡考量', '审慎乐观']


def gen_name(gender):
    last = random.choice(LAST_NAMES)
    first_pool = FIRST_MALE if gender == 'male' else FIRST_FEMALE
    first = random.choice(first_pool)
    if random.random() < 0.4:
        first += random.choice(first_pool)
    return last + first


def gen_avatar(seed, gender):
    h = hashlib.md5(seed.encode()).hexdigest()[:12]
    return f"https://api.dicebear.com/7.x/avataaars/svg?seed={h}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffd5dc,ffdfbf"


def gen_doctors(n=400):
    result = []
    for i in range(n):
        gender = random.choice(['male', 'female'])
        name = gen_name(gender)
        specialty = random.choice(list(SPECIALTIES.keys()))
        focus = random.choice(SPECIALTIES[specialty])

        tier_roll = random.random()
        if tier_roll < 0.3:
            city = random.choice(CITIES_TIER1); city_tier = 1
            hospital = random.choice(HOSPITALS[1]); htier = '三甲'
        elif tier_roll < 0.7:
            city = random.choice(CITIES_TIER2); city_tier = 2
            hospital = random.choice(HOSPITALS[2]); htier = random.choice(['三甲','三乙'])
        else:
            city = random.choice(CITIES_TIER3); city_tier = 3
            hospital = f"{city}市人民医院"; htier = random.choice(['二甲','三乙','三甲'])

        yrs = random.randint(5, 35)
        pvol = random.randint(50, 500) if yrs > 10 else random.randint(30, 200)

        innov_r = random.random()
        if innov_r < 0.1: innovation = 'innovator'
        elif innov_r < 0.3: innovation = 'early_adopter'
        elif innov_r < 0.7: innovation = 'majority'
        else: innovation = 'laggard'

        pubs = random.randint(0, 150) if yrs > 15 else random.randint(0, 30)
        trials = random.randint(0, 20) if yrs > 10 else random.randint(0, 5)

        attitude = random.choices(ATTITUDES_DOCTOR, weights=[0.15,0.3,0.25,0.2,0.1])[0]
        stance_map = {'积极推荐':'强烈建议纳入','支持使用':'建议纳入','谨慎推荐':'有条件支持','观望态度':'需更多数据','持保留意见':'暂不建议'}
        stance = stance_map.get(attitude, '需更多数据')

        # 扩展profile数据（存JSON）
        profile = {
            'avatar_url': gen_avatar(f"doc{i}{name}", gender),
            'bio': f"{specialty}专家，{yrs}年临床经验，专注于{focus}的诊治与研究。",
            'expertise': [specialty, focus],
            'influence_score': round(random.uniform(0.2, 0.95), 2),
            'title': random.choice(['主任医师','副主任医师','主治医师']) if yrs > 15 else random.choice(['主治医师','住院医师']),
            'department': f"{specialty}",
            'disease_focus': focus,
            'awards': random.choice(['无','省级科技进步奖','国家级课题负责人','SCI论文高被引']) if pubs > 30 else '无',
            'education': random.choice(['医学博士','医学硕士','博士后']) if yrs > 10 else random.choice(['医学硕士','医学学士']),
            'online_reputation': round(random.uniform(3.5, 5.0), 1),
            'patient_rating': round(random.uniform(3.0, 5.0), 1)
        }

        # DB字段（匹配schema）
        result.append({
            'agent_type': 'doctor',
            'name': name,
            'hospital': hospital,
            'hospital_tier': htier,
            'specialty': specialty,
            'years_experience': yrs,
            'patient_volume': pvol,
            'innovation_type': innovation,
            'publications': pubs,
            'clinical_trials': trials,
            'age': None,
            'gender': gender,
            'city': city,
            'city_tier': city_tier,
            'insurance_type': None,
            'income_level': None,
            'monthly_income': None,
            'primary_disease': None,
            'comorbidities': None,
            'expert_dimension': None,
            'university': None,
            'h_index': None,
            'total_publications': None,
            'industry_influence': None,
            'grant_count': None,
            'base_willingness': round(random.uniform(0.3, 0.9), 2),
            'attitude': attitude,
            'stance': stance,
            '_profile': profile  # 额外数据，不入库
        })
    return result


def gen_patients(n=1000):
    result = []
    for i in range(n):
        gender = random.choice(['male', 'female'])
        name = gen_name(gender)
        age = random.randint(25, 80)

        tier_roll = random.random()
        if tier_roll < 0.25:
            city = random.choice(CITIES_TIER1); city_tier = 1
        elif tier_roll < 0.6:
            city = random.choice(CITIES_TIER2); city_tier = 2
        else:
            city = random.choice(CITIES_TIER3); city_tier = 3

        inc_roll = random.random()
        if inc_roll < 0.2:
            income = 'high'; monthly = random.randint(15000, 50000)
        elif inc_roll < 0.6:
            income = 'middle'; monthly = random.randint(5000, 15000)
        else:
            income = 'low'; monthly = random.randint(2000, 5000)

        if city_tier == 1:
            ins = random.choice(['城镇职工','城镇职工','城镇居民'])
        elif city_tier == 2:
            ins = random.choice(['城镇职工','城镇居民','新农合'])
        else:
            ins = random.choice(['城镇居民','新农合','自费'])

        disease = random.choice(DISEASES)
        comorb = random.sample([d for d in DISEASES if d != disease], k=random.randint(0, 2))

        attitude = random.choices(ATTITUDES_PATIENT, weights=[0.2,0.3,0.25,0.15,0.1])[0]
        stance = random.choice(['希望用新药','听从医生建议','考虑经济因素','担心副作用'])

        tx_hx = random.choice(TREATMENT_HX)
        qol = round(random.uniform(0.3, 0.9), 2)

        profile = {
            'avatar_url': gen_avatar(f"pat{i}{name}", gender),
            'bio': f"{age}岁{'男' if gender=='male' else '女'}性，{disease}患者，居住于{city}。",
            'treatment_history': tx_hx,
            'quality_of_life': qol,
            'symptoms': random.sample(['疼痛','疲劳','食欲下降','睡眠障碍','焦虑','抑郁','呼吸困难','头晕'], k=random.randint(1,4)),
            'caregiver': random.choice(['配偶','子女','父母','自理','保姆']),
            'health_literacy': random.choice(['高','中','低']),
            'digital_literacy': random.choice(['熟练','一般','不熟悉']),
            'disease_duration_years': random.randint(1, 15) if age > 30 else random.randint(1, 5)
        }

        result.append({
            'agent_type': 'patient',
            'name': name,
            'hospital': None,
            'hospital_tier': None,
            'specialty': None,
            'years_experience': None,
            'patient_volume': None,
            'innovation_type': None,
            'publications': None,
            'clinical_trials': None,
            'age': age,
            'gender': gender,
            'city': city,
            'city_tier': city_tier,
            'insurance_type': ins,
            'income_level': income,
            'monthly_income': monthly,
            'primary_disease': disease,
            'comorbidities': ','.join(comorb) if comorb else None,
            'expert_dimension': None,
            'university': None,
            'h_index': None,
            'total_publications': None,
            'industry_influence': None,
            'grant_count': None,
            'base_willingness': round(random.uniform(0.2, 0.8), 2),
            'attitude': attitude,
            'stance': stance,
            '_profile': profile
        })
    return result


def gen_experts(n=400):
    result = []
    dims = list(EXPERT_DIMS.keys())
    per_dim = n // len(dims)
    remainder = n % len(dims)

    for di, dim in enumerate(dims):
        cnt = per_dim + (1 if di < remainder else 0)
        info = EXPERT_DIMS[dim]

        for i in range(cnt):
            gender = random.choice(['male', 'female'])
            name = gen_name(gender)

            if random.random() < 0.1:
                h_idx = random.randint(60, 120)
                title = random.choice(['院士', '长江学者', '教授'])
            elif random.random() < 0.3:
                h_idx = random.randint(30, 60)
                title = random.choice(['教授', '副教授', '研究员'])
            else:
                h_idx = random.randint(10, 30)
                title = random.choice(['副教授', '讲师', '助理研究员'])

            univ = random.choice(UNIVERSITIES)
            total_pubs = h_idx * random.randint(3, 8)
            grants = random.randint(1, 15) if h_idx > 20 else random.randint(0, 5)
            influence = 'high' if h_idx > 50 else ('medium' if h_idx > 25 else 'low')

            attitude = random.choice(ATTITUDES_EXPERT)
            stance = random.choice(['建议纳入', '需更多证据', '有条件支持', '建议观望'])

            profile = {
                'avatar_url': gen_avatar(f"exp{dim}{i}{name}", gender),
                'bio': f"{info['cn']}领域专家，{univ}{title}，H-index {h_idx}。",
                'expertise': [info['cn']] + info['focus'][:2],
                'influence_score': round(min(0.95, h_idx / 80), 2),
                'title': title,
                'dimension_name': info['cn'],
                'research_focus': ', '.join(random.sample(info['focus'], k=min(2, len(info['focus'])))),
                'keynote_speeches': random.randint(5, 50) if h_idx > 30 else random.randint(0, 10),
                'consulting_roles': random.choice(['国家药监局顾问', '医保局特聘专家', '卫健委咨询委员', '药学会理事', '无']) if h_idx > 40 else '无',
                'phd_students': random.randint(0, 30) if title in ['教授','院士','长江学者'] else random.randint(0, 5),
                'international_collab': random.sample(['哈佛', '斯坦福', '牛津', '约翰霍普金斯', 'WHO', 'FDA'], k=random.randint(0, 2)) if h_idx > 40 else []
            }

            result.append({
                'agent_type': 'expert',
                'name': name,
                'hospital': None,
                'hospital_tier': None,
                'specialty': None,
                'years_experience': None,
                'patient_volume': None,
                'innovation_type': None,
                'publications': None,
                'clinical_trials': None,
                'age': None,
                'gender': gender,
                'city': random.choice(CITIES_TIER1),
                'city_tier': 1,
                'insurance_type': None,
                'income_level': None,
                'monthly_income': None,
                'primary_disease': None,
                'comorbidities': None,
                'expert_dimension': dim,
                'university': univ,
                'h_index': h_idx,
                'total_publications': total_pubs,
                'industry_influence': influence,
                'grant_count': grants,
                'base_willingness': round(random.uniform(0.4, 0.95), 2),
                'attitude': attitude,
                'stance': stance,
                '_profile': profile
            })
    return result


def seed_agents(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("DELETE FROM agent_connections")
    c.execute("DELETE FROM agents")

    print("生成医生Agent...")
    doctors = gen_doctors(400)
    print(f"  ✓ {len(doctors)} 个医生")

    print("生成患者Agent...")
    patients = gen_patients(1000)
    print(f"  ✓ {len(patients)} 个患者")

    print("生成专家Agent...")
    experts = gen_experts(400)
    print(f"  ✓ {len(experts)} 个专家")

    all_agents = doctors + patients + experts
    print(f"\n总计: {len(all_agents)} 个Agent")

    # 提取profile数据单独保存
    profiles = {}
    db_columns = [k for k in all_agents[0].keys() if k != '_profile']

    print("\n写入数据库...")
    for agent in all_agents:
        aid = agent.get('id')
        profile = agent.pop('_profile')
        cols = ', '.join(db_columns)
        placeholders = ', '.join(['?'] * len(db_columns))
        vals = [agent[k] for k in db_columns]
        c.execute(f"INSERT INTO agents ({cols}) VALUES ({placeholders})", vals)
        # 获取刚插入的ID
        agent_id = c.lastrowid
        profiles[agent_id] = profile

    # 生成连接
    print("生成社交网络连接...")
    gen_connections(conn)

    conn.commit()
    conn.close()

    # 导出profile JSON
    export_dir = os.path.join(os.path.dirname(os.path.dirname(db_path)), 'docs', 'api')
    os.makedirs(export_dir, exist_ok=True)

    # agents.json - 基础数据 + profile
    print("\n导出JSON...")
    export_agents(db_path, profiles, export_dir)

    print("✅ 完成！")


def gen_connections(conn):
    c = conn.cursor()
    c.execute("SELECT id, agent_type, city, specialty FROM agents")
    rows = c.fetchall()

    by_city = {}
    by_type = {}
    by_specialty = {}
    for r in rows:
        aid, atype, city, spec = r
        by_type.setdefault(atype, []).append(aid)
        if city:
            by_city.setdefault(city, []).append(aid)
        if atype == 'doctor' and spec:
            by_specialty.setdefault(spec, []).append(aid)

    conns = set()

    # 同城连接
    for city, aids in by_city.items():
        for _ in range(min(len(aids) * 2, 80)):
            a, b = random.sample(aids, 2)
            conns.add((min(a,b), max(a,b), 'peer'))

    # 同专科连接
    for spec, aids in by_specialty.items():
        for _ in range(min(len(aids) * 3, 40)):
            a, b = random.sample(aids, 2)
            conns.add((min(a,b), max(a,b), 'kol'))

    # KOL影响（专家→医生）
    experts = by_type.get('expert', [])
    doctors = by_type.get('doctor', [])
    c.execute("SELECT id, city FROM agents WHERE agent_type='expert'")
    exp_cities = {r[0]: r[1] for r in c.fetchall()}
    c.execute("SELECT id, city FROM agents WHERE agent_type='doctor'")
    doc_cities = {r[0]: r[1] for r in c.fetchall()}

    for _ in range(200):
        eid = random.choice(experts)
        ecity = exp_cities.get(eid)
        same_city = [d for d in doctors if doc_cities.get(d) == ecity]
        if same_city:
            did = random.choice(same_city)
            conns.add((min(eid,did), max(eid,did), 'influence'))

    # 医生转诊
    for _ in range(150):
        a, b = random.sample(doctors, 2)
        conns.add((min(a,b), max(a,b), 'referral'))

    # 插入
    for a, b, ctype in conns:
        try:
            c.execute("INSERT OR IGNORE INTO agent_connections (agent_a, agent_b, connection_type, strength) VALUES (?,?,?,?)",
                     (a, b, ctype, round(random.uniform(0.3, 0.9), 2)))
        except:
            pass

    print(f"  ✓ {len(conns)} 条连接")


def export_agents(db_path, profiles, export_dir):
    """导出完整agent数据到JSON"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM agents ORDER BY id")
    agents = []
    for row in c.fetchall():
        agent = dict(row)
        pid = agent['id']
        if pid in profiles:
            agent['profile'] = profiles[pid]
        agents.append(agent)

    # 按类型分组
    by_type = {'doctor': [], 'patient': [], 'expert': []}
    for a in agents:
        by_type[a['agent_type']].append(a)

    # 导出
    out_path = os.path.join(export_dir, 'agents.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(agents),
            'doctors': len(by_type['doctor']),
            'patients': len(by_type['patient']),
            'experts': len(by_type['expert']),
            'agents': agents
        }, f, ensure_ascii=False, indent=2)

    print(f"  ✓ {out_path} ({len(agents)} agents)")

    # 导出连接
    c.execute("""
        SELECT ac.*, a1.name as name_a, a1.agent_type as type_a, a1.city as city_a,
               a2.name as name_b, a2.agent_type as type_b, a2.city as city_b
        FROM agent_connections ac
        JOIN agents a1 ON ac.agent_a = a1.id
        JOIN agents a2 ON ac.agent_b = a2.id
    """)
    connections = [dict(r) for r in c.fetchall()]

    conn_path = os.path.join(export_dir, 'connections.json')
    with open(conn_path, 'w', encoding='utf-8') as f:
        json.dump({'total': len(connections), 'connections': connections}, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {conn_path} ({len(connections)} connections)")

    conn.close()


if __name__ == '__main__':
    db_path = '/Users/apple/Desktop/PharmaSim/engine/data/pharmasim.db'
    seed_agents(db_path)
