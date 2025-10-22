#!/usr/bin/env python3
"""
تعبئة مواد POP المفقودة
"""

import sqlite3
from datetime import datetime

def populate_missing_pop_materials():
    """تعبئة مواد POP المفقودة"""
    print("📊 تعبئة مواد POP المفقودة...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # بيانات POP Materials حسب الموديل
        pop_materials_by_model = {
            'S95F': [
                'AI topper', 'OLED Topper', 'Glare Free', 'New Topper', '165 HZ Side POP',
                'Category POP', 'Samsung OLED Topper', '165 HZ & joy stick indicator',
                'AI Topper Gaming', 'Side POP', 'Specs Card', 'Why OLED side POP'
            ],
            'S90F': [
                'AI topper', 'OLED Topper', 'Glare Free', 'New Topper', 'Side POP',
                'Category POP', 'Samsung OLED Topper', 'Specs Card'
            ],
            'S85F': [
                'AI topper', 'OLED Topper', 'New Topper', 'Side POP', 'Specs Card'
            ],
            'QN90F': [
                'AI topper', 'Lockup Topper', 'Screen POP', 'New Topper', 'Glare Free', 'Specs Card'
            ],
            'QN85F': [
                'AI topper', 'Lockup Topper', 'Screen POP', 'New Topper', 'Specs Card'
            ],
            'QN80F': [
                'AI topper', 'Screen POP', 'New Topper', 'Specs Card'
            ],
            'QN70F': [
                'AI topper', 'Screen POP', 'New Topper', 'Specs Card'
            ],
            'Q8F': [
                'AI topper', 'Samsung QLED Topper', 'Screen POP', 'New Topper', 'Specs Card', 'QLED Topper'
            ],
            'Q7F': [
                'AI topper', 'Samsung QLED Topper', 'Screen POP', 'New Topper', 'Specs Card'
            ],
            'U8000': [
                'UHD topper', 'Samsung UHD topper', 'Screen POP', 'New Topper', 'Specs Card',
                'AI topper', 'Samsung Lockup Topper', 'Inch Logo side POP'
            ],
            '100"/98"': [
                'UHD topper', 'Samsung UHD topper', 'Screen POP', 'New Topper', 'Specs Card'
            ],
            'The Frame': [
                'Side POP', 'Matte Display', 'Category POP', 'Frame Bezel'
            ],
            'WD25DB8995': [
                'PODs (Door)', 'POD (Top)', 'POD (Front)', '3 PODs (Top)', 'AI Home POP',
                'AI Home', 'AI control panel', 'Capacity (Kg)', 'Capacity Dryer', 'Filter',
                'Ecobubble POP', 'Ecco Bubble', 'AI Ecco Bubble', '20 Years Warranty',
                'New Arrival', 'Samsung Brand/Tech Topper'
            ],
            'WD21D6400': [
                'PODs (Door)', 'POD (Top)', 'POD (Front)', 'AI Home POP', 'AI Home',
                'AI control panel', 'Capacity (Kg)', 'Filter', 'Ecobubble POP',
                '20 Years Warranty', 'Samsung Brand/Tech Topper'
            ],
            'WW11B1944DGB': [
                'PODs (Door)', 'POD (Top)', 'POD (Front)', '3 PODs (Top)', 'AI Home POP',
                'AI Home', 'AI control panel', 'Capacity (Kg)', 'Filter',
                'Ecobubble POP', '20 Years Warranty', 'Samsung Brand/Tech Topper'
            ],
            'WW11B1534D': [
                'PODs (Door)', 'POD (Top)', 'POD (Front)', 'AI Home POP', 'AI Home',
                'AI control panel', 'Capacity (Kg)', 'Filter', 'Ecobubble POP',
                '20 Years Warranty', 'Samsung Brand/Tech Topper'
            ],
            'WW90CGC': [
                'PODs (Door)', 'POD (Top)', 'AI Home POP', 'AI Home', 'AI control panel',
                'Capacity (Kg)', 'Filter', 'Ecobubble POP', '20 Years Warranty'
            ],
            'WW4040': [
                'POD (Top)', 'AI Home POP', 'Capacity (Kg)', 'Filter', 'Ecobubble POP', '20 Years Warranty'
            ],
            'WW4020': [
                'POD (Top)', 'AI Home POP', 'Capacity (Kg)', 'Filter', 'Ecobubble POP', '20 Years Warranty'
            ],
            'WA19CG6886': [
                'PODs (Door)', 'POD (Top)', 'POD (Front)', 'AI Home POP', 'AI Home',
                'AI control panel', 'Capacity (Kg)', 'Filter', 'Ecobubble POP',
                '20 Years Warranty', 'Samsung Brand/Tech Topper'
            ],
            'Local TL': [
                'POD (Top)', 'AI Home POP', 'Capacity (Kg)', 'Filter', 'Ecobubble POP'
            ],
            'RS70F': [
                'Samsung Brand/Tech Topper', 'Main POD', '20 Years Warranty',
                'Twin Cooling Plus™', 'Smart Conversion™', 'Digital Inverter™',
                'SpaceMax™', 'Tempered Glass', 'Power Freeze', 'Big Vegetable Box', 'Organize Big Bin'
            ],
            'Bespoke': [
                'Samsung Brand/Tech Topper', '20 Years Warranty', 'Key features POP', 'Side POP',
                'Global No.1', 'Freshness POP', 'Bacteria Safe Ionizer POP', 'Gallon Guard POP',
                'Big Vegetables Box POP', 'Adjustable Pin & Organize POP', 'Optimal Fresh',
                'Tempered Glass', 'Gallon Guard', 'Veg Box', 'Internal Display', 'Multi Tray',
                'Foldable Shelf', 'Active Fresh Filter'
            ],
            'TMF Non-Bespoke': [
                'Samsung Brand/Tech Topper', '20 Years Warranty', 'Key features POP', 'Side POP',
                'Global No.1', 'Freshness POP', 'Gallon Guard POP', 'Big Vegetables Box POP',
                'Adjustable Pin & Organize POP', 'Tempered Glass', 'Gallon Guard', 'Veg Box'
            ],
            'TMF': [
                'Samsung Brand/Tech Topper', '20 Years Warranty', 'Key features POP', 'Side POP',
                'Global No.1', 'Freshness POP', 'Gallon Guard POP', 'Big Vegetables Box POP'
            ],
            '(Bespoke, BMF)': [
                'Samsung Brand/Tech Topper', '20 Years Warranty', 'Key features POP', 'Side POP',
                'Global No.1', 'Led Lighting POP', 'Full Open Box POP', 'Big Guard POP',
                'Adjustable Pin', 'Saves Energy POP', 'Gentle Lighting', 'Multi Tray',
                'All-Around Cooling', '2 Step Foldable Shelf', 'Big Fresh Box'
            ],
            '(Non-Bespoke, BMF)': [
                'Samsung Brand/Tech Topper', '20 Years Warranty', 'Key features POP', 'Side POP',
                'Global No.1', 'Led Lighting POP', 'Full Open Box POP', 'Big Guard POP',
                'Saves Energy POP', 'Gentle Lighting', 'Multi Tray', 'All-Around Cooling'
            ],
            'Local TMF': [
                'Samsung Brand/Tech Topper', 'Key features POP', 'Side POP', 'Big Vegetables Box POP'
            ]
        }
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        added_count = 0
        
        for model_name, materials in pop_materials_by_model.items():
            # الحصول على معرف الموديل
            cursor.execute('SELECT id FROM models WHERE name = ?', (model_name,))
            model_result = cursor.fetchone()
            
            if model_result:
                model_id = model_result[0]
                print(f"📱 معالجة موديل: {model_name} (ID: {model_id})")
                
                for material in materials:
                    try:
                        # التحقق من وجود المادة
                        cursor.execute('SELECT COUNT(*) FROM pop_materials WHERE name = ? AND model_id = ?', 
                                     (material, model_id))
                        exists = cursor.fetchone()[0]
                        
                        if exists == 0:
                            # إدراج في الجدول الجديد
                            cursor.execute('''INSERT INTO pop_materials 
                                (name, model_id, created_at) VALUES (?, ?, ?)''',
                                (material, model_id, current_time))
                            added_count += 1
                            
                            # إدراج في الجدول القديم للتوافق
                            cursor.execute('''INSERT OR IGNORE INTO pop_materials_db 
                                (material_name, model_name, category_name, created_date) 
                                SELECT ?, ?, c.name, ?
                                FROM models m JOIN categories c ON m.category_id = c.id 
                                WHERE m.id = ?''',
                                (material, model_name, current_time, model_id))
                            
                            print(f"   ✅ أضيفت: {material}")
                        
                    except Exception as e:
                        print(f"   ⚠️ خطأ في إدراج المادة {material}: {e}")
            else:
                print(f"⚠️ لم يتم العثور على الموديل: {model_name}")
        
        conn.commit()
        print(f"\n✅ تم إضافة {added_count} مادة POP جديدة")
        
        # اختبار النتائج
        print("\n🧪 اختبار النتائج:")
        cursor.execute('''SELECT pm.name FROM pop_materials pm 
                         JOIN models m ON pm.model_id = m.id 
                         WHERE m.name = ?''', ('S95F',))
        materials = cursor.fetchall()
        print(f"🎨 مواد POP لموديل S95F: {len(materials)} مواد")
        for material in materials[:5]:
            print(f"   - {material[0]}")
        if len(materials) > 5:
            print(f"   ... و {len(materials) - 5} مواد أخرى")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تعبئة البيانات: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    populate_missing_pop_materials()