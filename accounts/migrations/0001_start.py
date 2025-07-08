# accounts/migrations/0002_create_initial_groups.py

import os
from django.db import migrations

def create_groups_and_admin(apps, schema_editor):
    """
    Creates the default user groups and an admin superuser
    by reading the settings from environment variables.
    """
    Group = apps.get_model('auth', 'Group')
    
    User = apps.get_model('auth', 'User')

    # --- Group Creation ---
    Group.objects.get_or_create(name='Director')
    Group.objects.get_or_create(name='Supervisor')
    print("Groups 'Director' and 'Supervisor' checked/created.")

    # --- Superuser Creation ---
    # Fetch credentials from environment variables
    username = os.getenv('DJANGO_SUPERUSER_USERNAME')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL')

    # Check if the essential variables have been defined
    if not all([username, password, email]):
        print("\nWARNING: Environment variables for superuser creation are not defined.")
        print("Superuser was not created. Please set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, and DJANGO_SUPERUSER_EMAIL.")
        return

    # Avoid creating the user if they already exist
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser: {username}")
        admin_user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=os.getenv('DJANGO_SUPERUSER_FIRST_NAME', ''), # Uses '' as default if not set
            last_name=os.getenv('DJANGO_SUPERUSER_LAST_NAME', '')  # Uses '' as default if not set
        )

        # Add the superuser to the Director group
        try:
            director_group = Group.objects.get(name='Director')
            admin_user.groups.add(director_group)
            print(f"User '{username}' added to the 'Director' group.")
        except Group.DoesNotExist:
            print("WARNING: Group 'Director' not found. Could not add the admin to the group.")
    else:
        print(f"Superuser '{username}' already exists. No action taken.")


def remove_groups(apps, schema_editor):
    """Function to reverse the migration"""
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Director', 'Supervisor']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length')
    ]

    operations = [
        migrations.RunPython(create_groups_and_admin, reverse_code=remove_groups),
    ]