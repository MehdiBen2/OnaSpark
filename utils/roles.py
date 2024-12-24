from enum import Enum

class UserRole:
    # Define all available roles
    ADMIN = 'Admin'
    ADMINISTRATEUR = 'administrateur'
    UNIT = 'unit'
    ZONE = 'zone'
    EMPLOYER = 'Employeur'
    DIRECTEUR_ZONE = 'Directeur de Zone'
    DIRECTEUR_UNITE = "Directeur d'Unité"

    # Role display names
    ROLE_NAMES = {
        ADMIN: 'Administrateur',
        ADMINISTRATEUR: 'Administrateur',
        UNIT: "Employeur de l'unité",
        ZONE: 'Employeur de zone',
        EMPLOYER: 'Employeur',
        DIRECTEUR_ZONE: 'Directeur de Zone',
        DIRECTEUR_UNITE: "Directeur d'Unité"
    }

    # Define role hierarchies and permissions
    ADMIN_ROLES = {ADMIN, ADMINISTRATEUR}  # Roles with full admin access
    DIRECTOR_ROLES = {DIRECTEUR_ZONE, DIRECTEUR_UNITE}  # Roles with director privileges
    UNIT_ROLES = {UNIT, EMPLOYER}  # Basic unit level roles

    @staticmethod
    def is_admin(role):
        """Check if role has admin privileges"""
        return role in UserRole.ADMIN_ROLES

    @staticmethod
    def is_director(role):
        """Check if role has director privileges"""
        return role in UserRole.DIRECTOR_ROLES

    @staticmethod
    def requires_unit(role):
        """Check if role requires unit assignment"""
        return role in UserRole.UNIT_ROLES

    @staticmethod
    def get_all_roles():
        """Get list of all available roles"""
        return [
            UserRole.UNIT,
            UserRole.ZONE,
            UserRole.EMPLOYER,
            UserRole.DIRECTEUR_ZONE,
            UserRole.DIRECTEUR_UNITE
        ]

    @staticmethod
    def get_role_name(role):
        """Get the display name for a role"""
        return UserRole.ROLE_NAMES.get(role, role)
