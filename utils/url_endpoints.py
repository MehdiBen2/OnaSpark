"""
Store all URL endpoints as constants to avoid hardcoding them in templates
"""

# Main routes
INDEX = 'index'
DASHBOARD = 'dashboard'
MAIN_DASHBOARD = 'main_dashboard'

# Incident routes
INCIDENT_LIST = 'incidents.incident_list'
NEW_INCIDENT = 'incidents.new_incident'
VIEW_INCIDENT = 'incidents.view_incident'
EDIT_INCIDENT = 'incidents.edit_incident'
DELETE_INCIDENT = 'incidents.delete_incident'
RESOLVE_INCIDENT = 'incidents.resolve_incident'
EXPORT_INCIDENT_PDF = 'incidents.export_incident_pdf'
EXPORT_ALL_INCIDENTS_PDF = 'incidents.export_all_incidents_pdf'
MERGE_INCIDENT = 'incidents.merge_incident'
BATCH_MERGE = 'incidents.batch_merge'

# Auth routes
LOGIN = 'auth.login'
LOGOUT = 'auth.logout'
REGISTER = 'auth.register'

# Profile routes
VIEW_PROFILE = 'profiles.view_profile'
EDIT_PROFILE = 'profiles.edit_profile'

# Unit routes
SELECT_UNIT = 'select_unit'
UPDATE_UNIT = 'update_unite'
GET_UNIT_INCIDENTS = 'get_unit_incidents'
