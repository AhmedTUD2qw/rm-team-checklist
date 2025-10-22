# Production Configuration

## Database Status
- Persistent data: ✅ Enabled
- Auto-backup: ✅ Enabled
- Data preservation: ✅ Enabled

## Security
- Admin user: Admin/ADMIN/admin123
- Change default password after deployment!

## Backup Schedule
- Manual backup: python production_setup.py backup
- Verify database: python production_setup.py verify

## Deployment Notes
- Database file: database.db (preserve this file)
- Backup directory: production_backups/
- Upload directory: static/uploads/

## Important
- Never delete database.db in production
- Regular backups are essential
- Monitor disk space for uploads
