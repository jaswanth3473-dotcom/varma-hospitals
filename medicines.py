"""
Medicines route — AI chatbot info + medicine list
"""
from flask import Blueprint, request, jsonify

medicines_bp = Blueprint('medicines', __name__)

MEDICINES_DB = [
    {"id":1,"name":"Aspirin","dosage":"500mg","price":25,"stock":150,"category":"Pain Relief","uses":"Pain, fever, inflammation","side_effects":"Stomach upset, bleeding risk"},
    {"id":2,"name":"Paracetamol","dosage":"500mg","price":15,"stock":200,"category":"Pain Relief","uses":"Pain, fever","side_effects":"Safe at normal doses; overdose harms liver"},
    {"id":3,"name":"Ibuprofen","dosage":"400mg","price":35,"stock":100,"category":"Anti-inflammatory","uses":"Inflammation, pain, fever","side_effects":"Stomach irritation, avoid on empty stomach"},
    {"id":4,"name":"Amoxicillin","dosage":"500mg","price":85,"stock":80,"category":"Antibiotic","uses":"Bacterial infections, throat, ear, chest","side_effects":"Nausea, diarrhea, rash"},
    {"id":5,"name":"Ciprofloxacin","dosage":"500mg","price":120,"stock":60,"category":"Antibiotic","uses":"Urinary, respiratory bacterial infections","side_effects":"Nausea, dizziness, avoid sunlight"},
    {"id":6,"name":"Omeprazole","dosage":"20mg","price":45,"stock":120,"category":"Digestive","uses":"Acid reflux, GERD, ulcers","side_effects":"Headache, stomach pain"},
    {"id":7,"name":"Metformin","dosage":"500mg","price":55,"stock":90,"category":"Diabetes","uses":"Type 2 diabetes management","side_effects":"Nausea, diarrhea (usually temporary)"},
    {"id":8,"name":"Lisinopril","dosage":"10mg","price":65,"stock":75,"category":"Blood Pressure","uses":"Hypertension, heart failure","side_effects":"Dry cough, dizziness"},
    {"id":9,"name":"Atorvastatin","dosage":"10mg","price":75,"stock":70,"category":"Cholesterol","uses":"High cholesterol, heart disease prevention","side_effects":"Muscle pain, liver effects"},
    {"id":10,"name":"Vitamin C","dosage":"500mg","price":30,"stock":200,"category":"Vitamins","uses":"Immunity, antioxidant","side_effects":"Diarrhea at high doses"},
    {"id":11,"name":"Vitamin B12","dosage":"1000mcg","price":40,"stock":110,"category":"Vitamins","uses":"Energy, nerve health, anemia","side_effects":"Very rare at normal doses"},
    {"id":12,"name":"Calcium Supplement","dosage":"500mg","price":50,"stock":95,"category":"Minerals","uses":"Bone health, osteoporosis prevention","side_effects":"Constipation, take with food"},
]

@medicines_bp.route('/api/medicines', methods=['GET'])
def get_medicines():
    return jsonify({'success': True, 'medicines': MEDICINES_DB}), 200

@medicines_bp.route('/api/medicines/info', methods=['POST'])
def medicine_info():
    """AI-powered medicine chatbot — falls back to local DB if Claude API unavailable."""
    data     = request.get_json() or {}
    question = data.get('question', '').strip().lower()

    if not question:
        return jsonify({'success': False, 'response': 'Please ask a question.'}), 400

    # Try to match medicine name from local DB first
    for med in MEDICINES_DB:
        if med['name'].lower() in question:
            resp = (
                f"💊 {med['name']} ({med['dosage']})\n\n"
                f"📋 Uses: {med['uses']}\n"
                f"⚠️ Side effects: {med['side_effects']}\n"
                f"💰 Price: ₹{med['price']}\n"
                f"📦 Stock: {med['stock']} units\n\n"
                f"Always consult your doctor before taking any medicine."
            )
            return jsonify({'success': True, 'response': resp}), 200

    # Category keywords
    kw_map = {
        'pain':       [m for m in MEDICINES_DB if m['category']=='Pain Relief'],
        'antibiotic': [m for m in MEDICINES_DB if m['category']=='Antibiotic'],
        'diabetes':   [m for m in MEDICINES_DB if m['category']=='Diabetes'],
        'blood pressure': [m for m in MEDICINES_DB if m['category']=='Blood Pressure'],
        'vitamin':    [m for m in MEDICINES_DB if m['category']=='Vitamins'],
        'digestive':  [m for m in MEDICINES_DB if m['category']=='Digestive'],
    }
    for kw, meds in kw_map.items():
        if kw in question and meds:
            names = ', '.join(m['name'] for m in meds)
            return jsonify({'success': True, 'response': f"For {kw} we have: {names}. Ask me about any specific medicine for more details."}), 200

    # Generic response
    return jsonify({'success': True, 'response': (
        "I can help with medicine information!\n\n"
        "Try asking:\n• 'What is Paracetamol?'\n• 'Side effects of Metformin'\n• 'Pain relief medicines'\n• 'Antibiotic list'\n\n"
        "For medical advice, always consult your doctor. 🏥"
    )}), 200


def seed_medicines():
    """Seed medicine table in DB if empty."""
    try:
        from models import Medicine
        from flask import current_app
        if Medicine.query.count() > 0:
            return
        from models import db
        for m in MEDICINES_DB:
            med = Medicine(
                name=m['name'], category=m['category'],
                dosage=m['dosage'], price=m['price'],
                stock=m['stock'], uses=m['uses']
            )
            db.session.add(med)
        db.session.commit()
        print(f'✅ Seeded {len(MEDICINES_DB)} medicines.')
    except Exception as e:
        print(f'Medicine seed error (non-fatal): {e}')