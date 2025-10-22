#!/usr/bin/env python3
"""
تعبئة البيانات الافتراضية للنظام النظيف
"""

import sqlite3
from datetime import datetime

def populate_clean_data():
    """تعبئة البيانات الافتراضية"""
    print("📊 تعبئة البيانات الافتراضية...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # تعبئة الموديلات
        models_data = {
            'OLED': ['S95F', 'S90F', 'S85F'],
            'Neo QLED': ['QN90F', 'QN85F', 'QN80F', 'QN70F'],
            'QLED': ['Q8F', 'Q7F'],
            'UHD': ['U8000', '100"/98"'],
            'LTV': ['The Frame'],
            'BESPOKE COMBO': ['WD25DB8995', 'WD21D6400'],
            'BESPOKE Front': ['WW11B1944DGB'],
            'Front': ['WW11B1534D', 'WW90CGC', 'WW4040', 'WW4020'],
            'TL': ['WA19CG6886', 'Local TL'],
            'SBS': ['RS70F'],
            'TMF': ['Bespoke', 'TMF Non-Bespoke', 'TMF'],
            'BMF': ['(Bespoke, BMF)', '(Non-Bespoke, BMF)'],
            'Local TMF': ['Local TMF']
        }
        
        for category_name, model_list in models_data.items():
            # الحصول على معرف الفئة
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            category_result = cursor.fetchone()
            if category_result:
                category_id = category_result[0]
                
                for model_name in model_list:
                    cursor.execute('INSERT OR IGNORE INTO models (name, category_id, created_at) VALUES (?, ?, ?)',
                                 (model_name, category_id, current_time))
        
        # تعبئة أنواع العرض
        display_types_data = {
            'OLED': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
            'Neo QLED': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
            'QLED': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
            'UHD': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
            'LTV': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
            'BESPOKE COMBO': ['POP Out', 'POP Inner', 'POP'],
            'BESPOKE Front': ['POP Out', 'POP Inner', 'POP'],
            'Front': ['POP Out', 'POP Inner', 'POP'],
            'TL': ['POP Out', 'POP Inner', 'POP'],
            'SBS': ['POP Out', 'POP Inner', 'POP'],
            'TMF': ['POP Out', 'POP Inner', 'POP'],
            'BMF': ['POP Out', 'POP Inner', 'POP'],
            'Local TMF': ['POP Out', 'POP Inner', 'POP']
        }
        
        for category_name, display_list in display_types_data.items():
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            category_result = cursor.fetchone()
            if category_result:
                category_id = category_result[0]
                
                for display_name in display_list:
                    cursor.execute('INSERT OR IGNORE INTO display_types (name, category_id, created_at) VALUES (?, ?, ?)',
                                 (display_name, category_id, current_time))
        
        # تعبئة مواد POP
        pop_materials_data = {
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
        
        for model_name, materials in pop_materials_data.items():
            cursor.execute('SELECT id FROM models WHERE name = ?', (model_name,))
            model_result = cursor.fetchone()
            if model_result:
                model_id = model_result[0]
                
                for material in materials:
                    cursor.execute('INSERT OR IGNORE INTO pop_materials (name, model_id, created_at) VALUES (?, ?, ?)',
                                 (material, model_id, current_time))
        
        conn.commit()
        
        # إحصائيات
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM models")
        models_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM display_types")
        display_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pop_materials")
        pop_count = cursor.fetchone()[0]
        
        print(f"✅ تم تعبئة البيانات:")
        print(f"   📊 الفئات: {categories_count}")
        print(f"   📱 الموديلات: {models_count}")
        print(f"   🖥️ أنواع العرض: {display_count}")
        print(f"   🎨 مواد POP: {pop_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تعبئة البيانات: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    populate_clean_data()