# Boat Booking System - Login Credentials

## Generated on: 2026-01-28

This file contains all login credentials for the seeded database. Run `python seed.py` to generate this data.

---

## Admin Account

| Role | Username | Password | Email |
|------|----------|----------|-------|
| Admin | `admin` | `admin123` | admin@boatbooking.com |

---

## Regular Users (5 Users)

| Username | Password | Email |
|----------|----------|-------|
| `kiran` | `password123` | kiran@gmail.com |
| `Saro` | `password123` | saro@gmail.com |
| `Sachin` | `password123` | sachin@gmail.com |
| `akash` | `password123` | akash@gmail.com |
| `abdul` | `password123` | abdul@gmail.com |

---

## Vendor Accounts (5 Vendors)

| Username | Password | Email | Business Name | Location |
|----------|----------|-------|---------------|----------|
| `vendor1` | `vendor123` | vendor1@example.com | Marina Deluxe | Goa |
| `vendor2` | `vendor123` | vendor2@example.com | Beach Boats Co | Kerala |
| `vendor3` | `vendor123` | vendor3@example.com | River Sports | Maharashtra |
| `vendor4` | `vendor123` | vendor4@example.com | Yacht Rentals | Gujarat |
| `vendor5` | `vendor123` | vendor5@example.com | Island Tours | Andaman |

---

## Seeded Data Summary

### Users
- **Total Users:** 5
- **All users have password:** `password123`

### Vendors
- **Total Vendors:** 5
- **All vendors have password:** `vendor123`
- **Status:** All approved ✓

### Boats
- **Total Boats:** 35 (7 categories × 5 vendors)
- **Categories:** 
  - Speed Boat (High-speed performance boat)
  - Luxury Yacht (Luxurious yacht for premium experience)
  - Fishing Boat (Equipped for fishing expeditions)
  - Houseboat (Comfortable houseboat for accommodation)
  - Party Boat (Perfect for celebrations and groups)
  - Tour Boat (Great for sightseeing tours)
  - Diving Boat (Equipped for diving and snorkeling)
- **Each vendor has:** 1 boat of each category
- **Locations:** Goa, Kerala, Maharashtra, Gujarat, Andaman
- **Pricing:** Varies by category (₹800-₹3000 per hour, ₹4500-₹15000 per day)

### Bookings
- **Total Bookings:** 15 (3 per user)
- **Completed Bookings:** 10 (2 per user)
- **Active Bookings:** 5 (1 per user)
- **Boat Categories Covered:** All 8 categories represented in bookings

### Reviews
- **Total Reviews:** 10 (one for each completed booking)
- **Ratings:** Mix of 4 and 5 stars
- **Coverage:** Reviews for all boats with completed bookings across all categories

### Payments
- **Total Payment Records:** 15
- **Methods:** Mix of Card, UPI, and Wallet
- **Status:** All successful ✓

---

## Quick Login Guide

1. **Admin Access:**
   - Navigate to: `http://localhost:5000/admin`
   - Username: `admin` | Password: `admin123`

2. **Vendor Access:**
   - Navigate to: `http://localhost:5000/vendor/login`
   - Username: `vendor1` (or any vendor1-vendor5) | Password: `vendor123`

3. **User Access:**
   - Navigate to: `http://localhost:5000/login`
   - Username: `kiran`, `Saro`, `Sachin`, `akash`, or `abdul` | Password: `password123`

---

## Features Included in Seeded Data

✓ All boat categories for every vendor  
✓ Mix of completed and active bookings  
✓ Review system with ratings for completed bookings  
✓ Payment records for all bookings  
✓ Boat images (placeholder paths - can be updated later)  
✓ Multiple locations across India  

---

## How to Use This Data

1. Run the seeding script:
   ```bash
   python seed.py
   ```

2. The script will:
   - Clear all existing data
   - Create 1 admin + 5 users + 5 vendors
   - Create 35 boats (7 categories × 5 vendors)
   - Create 15 bookings (10 completed, 5 active)
   - Create 10 reviews with ratings
   - Create 15 payment records

3. Start the application:
   ```bash
   python run.py
   ```

4. Login with any credentials from above

---

## Boat Categories & Pricing

| Category | Capacity | Price/Hour | Price/Day | Description |
|----------|----------|-----------|----------|-------------|
| Speed Boat | 8 | ₹1,500 | ₹8,000 | High-speed performance boat |
| Luxury Yacht | 12 | ₹3,000 | ₹15,000 | Luxurious yacht for premium experience |
| Fishing Boat | 6 | ₹800 | ₹4,500 | Equipped for fishing expeditions |
| Houseboat | 10 | ₹2,000 | ₹10,000 | Comfortable houseboat for accommodation |
| Party Boat | 15 | ₹1,800 | ₹9,000 | Perfect for celebrations and groups |
| Tour Boat | 12 | ₹1,200 | ₹6,500 | Great for sightseeing tours |
| Diving Boat | 8 | ₹1,600 | ₹8,500 | Equipped for diving and snorkeling |

## Notes

- **Boat Images:** Placeholder paths set. Update images in `/static/uploads/boats/` directory and database later.
- **Passwords:** Users use `password123`, vendors use `vendor123`, admin uses `admin123`
- **Timestamps:** Bookings created with past/future dates for realistic testing
- **Reviews:** Created only for completed bookings with 4-5 star ratings
- **Payments:** All payment records marked as successful
- **Vendors:** All pre-approved and active
- **Categories:** 7 boat types matching the system's filter dropdown (Speed Boat, Luxury Yacht, Fishing Boat, Houseboat, Party Boat, Tour Boat, Diving Boat)

