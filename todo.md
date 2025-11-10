Below is a **clean, feature-only checklist** derived from your markdown.  
Everything is grouped exactly as in the original TODO, but **no code, no implementation details** – just the features you want to build with **Django + HTMX/ReactJS**.

---

# Travel Marketplace – Feature List (Django + HTMX/ReactJS)

## below are completed

django-admin startproject travel_marketplace
cd travel_marketplace

python manage.py startapp users
python manage.py startapp agents
python manage.py startapp requirements
python manage.py startapp quotes
python manage.py startapp bookings
python manage.py startapp messages
python manage.py startapp notifications
python manage.py startapp payments
python manage.py startapp reviews
python manage.py startapp media
python manage.py startapp pages
python manage.py startapp ai_assistant
python manage.py startapp admin_panel

### Backend Collections

- Users (with auth)
- Agents (company info, verification, specializations)
- Requirements (flight, hotel, bus, train, tour package details)
- Quotes (pricing, inclusions, itinerary)
- Bookings
- Messages
- Notifications
- Payments
- Reviews
- Media
- Categories & Pages

### Tech Stack Setup

- **Django + HTMX/ReactJS**
- SQLite database adapter
- Lexical rich text editor
- TypeScript configuration → **Python typing / Django models**
- Tailwind CSS + Shadcn/UI
- Authentication system

---

## RECENTLY ADDED ✨

### AI Features

- AI Travel Assistant chatbot page
- Conversational requirement gathering
- Auto-generated itineraries
- Booking.com-inspired modern design
- [ ] Integrate real AI API (OpenAI/Anthropic)
- [ ] Save AI conversations to database
- [ ] Convert AI chat to formal requirement
- [ ] AI-powered price predictions
- [ ] Smart destination recommendations

---

## TODO – PRIORITY ORDER 🎯

### PHASE 1: Commission System (CRITICAL) ✅

- 2% commission from agents, 1% from customers
- Commission fields in Bookings:
  - `agentCommission` (2% of booking amount)
  - `customerCommission` (1% of booking amount)
  - `platformCommission` (total)
  - `agentPayout` (booking – agentCommission)
- Auto-calculate commissions on booking save
- Update agent earnings on booking confirmation
- Agent collection fields:
  - `totalEarnings`
  - `pendingPayout`
  - `paidOut`
  - `commissionRate` (default 2%)
- Global Settings for:
  - Agent commission rate (default 2%)
  - Customer commission rate (default 1%)
  - Minimum payout threshold
  - Payout schedule

---

### PHASE 2: User Frontend Pages

#### A. Homepage & Navigation ✅

- Landing page with:
  - Hero section (travel types)
  - How it works
  - Featured destinations
  - Testimonials
- Navigation header with:
  - “Submit Requirement” CTA
  - User profile dropdown
  - Notifications icon

#### B. Requirement Submission Flow ✅

- `/requirements/new` page
- Service type selector (Flight / Hotel / Bus / Train / Package)
- Dynamic form per service type
- Form validation & submission

#### C. User Dashboard ✅

- `/dashboard` overview
  - Stats: active requirements, quotes, bookings
  - Recent activity feed
- `/dashboard/requirements`
  - List all user requirements
  - Filter by status, type, date
  - View details & quote count

#### D. Quote Management

- `/dashboard/requirements/[id]`
  - Requirement details
  - List of received quotes
  - Quote comparison table
  - Accept / Reject actions
  - Chat with agent
- Quote comparison UI
  - Side-by-side view
  - Highlight best price
  - Show agent rating
  - Expandable itinerary

#### E. Booking & Payment

- `/booking/[quoteId]`
  - Quote summary
  - Traveler details form
  - Payment method selection
  - Terms & conditions
- PayPal payment gateway
  - SDK integration
  - Payment processing
  - Success/failure handling
  - Booking confirmation
- `/booking/success`
  - Confirmation page
  - Download invoice/voucher
  - Share booking

#### F. My Bookings

- `/dashboard/bookings`
  - Tabs: Upcoming / Past / Cancelled
  - Filter & search
- `/dashboard/bookings/[id]`
  - Booking details
  - Traveler info
  - Payment history
  - Download vouchers
  - Contact agent
  - Write review (post-trip)

---

### PHASE 3: Agent Frontend Pages

#### A. Agent Registration

- `/agent/register`
  - Company info form
  - Document upload (GST, PAN, Trade License)
  - Specialization selection
  - Submit for verification
- `/agent/verification-pending`
  - Status message
  - Next steps
  - Contact admin

#### B. Agent Dashboard

- `/agent/dashboard`
  - Stats: pending quotes, leads, revenue
  - Recent requirements feed
  - Quick actions
- `/agent/requirements`
  - Browse all open requirements
  - Filters: type, budget, date, destination
  - “Mark as Interested”
  - View requirement details

#### C. Quote Builder

- `/agent/requirements/[id]/quote`
  - Requirement summary
  - Quote form (price, inclusions, exclusions)
  - Itinerary builder (rich text)
  - Upload documents
  - Set validity period
  - Submit quote
- Quote templates
  - Save & reuse common structures
  - Quick-fill from template

#### D. Agent Bookings

- `/agent/bookings`
  - Active / Completed tabs
  - Upload vouchers/tickets
  - Update status
- `/agent/bookings/[id]`
  - Booking details
  - Customer info
  - Upload documents
  - Mark as completed

#### E. Earnings & Payouts

- `/agent/earnings`
  - Earnings overview
  - Pending payout
  - Payout history
  - Commission breakdown
  - Generate invoice
- Payout request system
  - Request payout button
  - Minimum threshold check
  - Bank details form
  - Admin approval workflow

---

### PHASE 4: Communication System

#### A. In-App Messaging

- Messages UI component
  - Chat interface
  - Real-time updates (polling/websockets)
  - File attachments
  - Message notifications
- `/messages`
  - Conversation list
  - Unread badges
  - Search
- `/messages/[requirementId]`
  - Chat thread
  - Send message
  - Upload files
  - Requirement context

#### B. Notifications System

- Notification dropdown
  - Unread count
  - Mark as read
  - Types: quote, booking, message, payment
  - Click-to-navigate
- `/notifications`
  - Full list
  - Filter by type
  - Mark all as read

#### C. Email Notifications

- Email service (Nodemailer)
- Templates:
  - New requirement
  - Quote received
  - Quote accepted
  - Booking confirmed
  - Payment received
  - Review request

---

### PHASE 5: Admin Panel Enhancements

#### A. Dashboard Analytics

- Custom admin dashboard
  - Total users, agents, requirements, bookings
  - Revenue charts
  - Conversion rates
  - Recent activities
- API endpoints:
  - `/api/admin/stats`
  - `/api/admin/revenue`
  - `/api/admin/conversion-rates`

#### B. Agent Verification

- Verification workflow
  - Pending agents list
  - View documents
  - Approve / Reject with reason
  - Notify agent

#### C. Commission Management

- Commission dashboard
  - Total platform revenue
  - Pending agent payouts
  - Customer commissions
  - Monthly/yearly reports
- Payout management
  - Pending requests
  - Approve / Reject
  - Process payment
  - Payout history

#### D. Dispute Resolution

- Dispute fields in Bookings:
  - `disputeStatus` (none/raised/in-review/resolved)
  - `disputeReason`
  - `disputeResolution`
- Dispute management page
  - View all disputes
  - Assign to admin
  - Communicate with parties
  - Resolve

---

### PHASE 6: Additional Features

#### A. Reviews & Ratings

- Review submission form
  - Star rating (1–5)
  - Written review
  - Photo upload
  - Submit after trip
- Agent profile reviews
  - Average rating
  - Review list
  - Filter by rating
  - Verified badge

#### B. Search & Filters

- Advanced requirement search
  - Destination, dates, budget, type
- Agent directory
  - Search by specialization
  - Filter by rating
  - Sort by bookings

#### C. User Profile

- `/profile`
  - Edit personal info
  - Change password
  - Travel preferences
  - Notification settings
- `/profile/settings`
  - Email / SMS preferences
  - Privacy settings

#### D. Mobile Responsiveness

- Fully responsive layouts
- Touch-friendly UI
- Mobile navigation menu
- Cross-device testing

---

### PHASE 7: Amadeus API Integration

#### A. Amadeus API Setup

- Developer account & credentials
- OAuth token management
- Environment variables

#### B. Flight Search

- Flight Offers Search API
  - Origin/destination/dates
  - Filters: cabin, airline, stops
  - Real-time pricing
- Flight Offers Price API
  - Price confirmation
  - Fare rules
- Flight search UI
  - Airport autocomplete
  - Results with filters
  - Flight details (duration, stops, baggage)

#### C. Hotel Search

- Hotel Search API
  - City/location search
  - Filters: stars, amenities, price
- Hotel Booking API
  - Room availability
  - Booking flow
- Hotel search UI
  - Map integration
  - Hotel cards with images
  - Filters & sorting
  - Hotel detail page

#### D. Additional Amadeus APIs

- Airport & City Search (autocomplete)
- Flight Inspiration Search (budget-based suggestions)
- Hotel Ratings API (sentiment & reviews)
- Points of Interest API (attractions near hotels)

#### E. Agent Quote Enhancement

- Agents access Amadeus data in quote builder
- Pre-fill pricing from Amadeus
- Add markup/commission
- Compare agent quote vs live Amadeus price

#### F. Caching & Performance

- Cache API responses
- Rate limiting
- Background price updates
- Webhook for booking status

---

### PHASE 8: Testing & Deployment

#### A. Testing

- Integration tests (Vitest → **Django tests**)
  - API endpoints
  - CRUD operations
  - Commission logic
- E2E tests (Playwright)
  - Registration → Requirement → Quote → Payment → Booking
  - Agent quote flow

#### B. Security

- Rate limiting
- CSRF protection
- Input sanitization
- Secure file uploads
- Env validation

#### C. Performance

- Image optimization
- Caching strategy
- Database indexing
- Code splitting
- Lazy loading

#### D. Deployment

- Production DB (PostgreSQL)
- CI/CD pipeline
- Hosting (Vercel/Railway/AWS)
- Domain + SSL
- Email service config
- PayPal production keys

---

## IMMEDIATE NEXT FEATURES (Start Here)

1. **Commission System**
2. **User Requirement Submission** (`/requirements/new` + dynamic forms)
3. **User Dashboard** (overview + requirements list)
4. **Agent Dashboard** (requirements feed + quote builder)
5. **Payment Integration** (PayPal flow)
6. **Amadeus API** (flight/hotel search – later phase)

---

**Tech Stack (Final)**

- **Backend:** Django
- **Frontend:** HTMX + ReactJS
- **Styling:** Tailwind CSS + Shadcn/UI
- **Auth:** Django Auth / Custom
- **Payment:** PayPal
- **Email:** Nodemailer

---

**Focus Areas**

- All collections ready
- Build **user → agent → admin** flows
- Commission = core revenue
- Payment = MVP gate
- Amadeus = real-time data (Phase 7)

---

**All features listed. No code. Ready for Django + HTMX/ReactJS implementation.**
