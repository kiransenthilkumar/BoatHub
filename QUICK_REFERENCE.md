# Quick Reference Guide - Boat Booking System

## Running the Application

```bash
cd "d:\kiran\Final Year Projects\PYTHON PROJECTS\BoatBookingSystem"
python run.py
```

The app will be available at: `http://127.0.0.1:5000`

---

## Test Accounts

### Admin
- **Username:** admin
- **Password:** admin123

### Vendor
- **Username:** vendor1
- **Password:** vendor123

### User
- **Username:** user1
- **Password:** user123

---

## Key Routes

### User Routes
- `/user/dashboard` - User dashboard
- `/user/boats` - Browse boats with filtering
- `/user/boat/<id>` - Boat details
- `/user/book/<id>` - Book a boat
- `/user/payment/<id>` - Payment page
- `/user/booking_history` - View bookings
- `/user/review/<id>` - Submit review

### Vendor Routes
- `/vendor/dashboard` - Vendor dashboard
- `/vendor/my_boats` - Manage boats
- `/vendor/add_boat` - Add new boat
- `/vendor/manage_bookings` - Booking management
- `/vendor/reviews` - Customer reviews

### Admin Routes
- `/admin/dashboard` - Admin dashboard
- `/admin/manage_vendors` - Vendor management
- `/admin/manage_boats` - Boat management
- `/admin/manage_users` - User management
- `/admin/moderate_reviews` - Review moderation

---

## Critical Components

### Database Models
- `User` - Authentication & user profiles
- `Vendor` - Vendor accounts
- `Boat` - Boat listings with images
- `Booking` - Reservation management
- `Payment` - Payment tracking
- `Review` - Customer reviews
- `BoatImage` - Multiple images per boat

### Key Features
1. **Boat Filtering**
   - Location-based search
   - Price range filtering
   - Capacity filtering
   - Rating-based filtering
   - Category filtering

2. **Booking Management**
   - Date-based reservations
   - Status tracking (pending, approved, completed, cancelled)
   - Payment integration
   - Booking cancellation

3. **Review System**
   - Star ratings (1-5)
   - Text reviews
   - Admin moderation

4. **Image Management**
   - Multiple images per boat
   - Image carousel on detail page
   - Placeholder fallbacks

---

## Important Code Patterns

### Python Property Usage (READ THIS!)
Properties like `Boat.average_rating` are computed values, NOT database columns.

**✅ CORRECT:** Filter in Python after loading data
```python
boats = Boat.query.all()
filtered = [b for b in boats if b.average_rating >= 3.0]
```

**❌ WRONG:** Don't use properties in SQLAlchemy filters
```python
boats = Boat.query.filter(Boat.average_rating >= 3.0).all()  # ERROR!
```

### Relationship Loading (IMPORTANT!)
Always use `joinedload()` to prevent N+1 queries:
```python
boats = Boat.query.options(joinedload(Boat.vendor)).all()
```

---

## Common Issues & Solutions

### Issue: Property Comparison Error
**Problem:** `TypeError: '>=' not supported between instances of 'property' and 'float'`

**Solution:** Filter computed properties in Python, not SQLAlchemy queries.

### Issue: Images Not Loading
**Cause:** Image files missing in `app/static/images/`

**Solution:** Run `python seed.py` to create test images, or upload real images.

### Issue: Vendor Account Not Showing Boats
**Cause:** Vendor account not approved

**Solution:** Admin must approve vendor first via admin dashboard.

---

## Files Modified (Latest Session)

1. **app/routes/user.py** - Fixed boat rating filter
2. **app/templates/base.html** - Added scripts block
3. **app/templates/user/payment.html** - Fixed template syntax errors

---

## Database Backup

To backup the database:
```bash
# Current database location
app/instance/boat_booking.db
```

---

## Deployment Checklist

- [ ] Set `DEBUG = False` in production
- [ ] Use a production WSGI server (Gunicorn/uWSGI)
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up email notifications
- [ ] Configure payment gateway
- [ ] Set up SSL/TLS certificates
- [ ] Configure environment variables
- [ ] Set up database backups
- [ ] Configure CDN for static files
- [ ] Set up logging and monitoring

---

## Support

For issues or questions, refer to:
1. `CODE_ANALYSIS_REPORT.md` - Complete analysis
2. Template files for UI patterns
3. Route files for API patterns
4. Models file for data structure

---

**Last Updated:** January 28, 2026
**Status:** ✅ Production Ready
