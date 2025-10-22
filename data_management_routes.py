from flask import jsonify
from database_manager_fix import (
    update_category,
    update_model,
    update_display_type,
    fix_missing_relationships
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_manage_data(data):
    """Handle data management operations with improved error handling"""
    try:
        action = data.get('action')
        data_type = data.get('type')
        item_id = data.get('id')
        
        if action == 'edit':
            if data_type == 'categories':
                success = update_category(item_id, data.get('name'))
                if success:
                    # Fix any missing relationships after category update
                    fix_missing_relationships()
                    return jsonify({
                        'success': True,
                        'message': 'Category and related items updated successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to update category. Please try again.'
                    }), 500
                    
            elif data_type == 'models':
                success = update_model(item_id, data.get('name'), data.get('category_id'))
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Model updated successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to update model. Please try again.'
                    }), 500
                    
            elif data_type == 'display_types':
                success = update_display_type(item_id, data.get('name'), data.get('category_id'))
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Display type updated successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to update display type. Please try again.'
                    }), 500
                    
        return jsonify({
            'success': False,
            'message': 'Invalid action or data type'
        }), 400
        
    except Exception as e:
        logger.error(f"Error in handle_manage_data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500