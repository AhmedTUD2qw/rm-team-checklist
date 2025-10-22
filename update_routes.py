from database_utils import update_category, update_model, update_display_type
import logging

# Add these routes to your app.py

@app.route('/update_categories/<int:id>', methods=['POST'])
def update_category_route(id):
    """Update category and cascade changes"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'success': False, 'message': 'Missing name in request'}), 400
            
        result = update_category(id, data['name'])
        if result:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to update category'}), 500
            
    except Exception as e:
        logging.error(f"Error in update_category_route: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/update_models/<int:id>', methods=['POST'])
def update_model_route(id):
    """Update model with category relationship"""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'category_id' not in data:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
        result = update_model(id, data['name'], data['category_id'])
        if result:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to update model'}), 500
            
    except Exception as e:
        logging.error(f"Error in update_model_route: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/update_display_types/<int:id>', methods=['POST'])
def update_display_type_route(id):
    """Update display type with category relationship"""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'category_id' not in data:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
        result = update_display_type(id, data['name'], data['category_id'])
        if result:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to update display type'}), 500
            
    except Exception as e:
        logging.error(f"Error in update_display_type_route: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500