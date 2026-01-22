# Booking Flow Diagram

## 📊 Complete Booking Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INITIATES BOOKING                       │
│              "I want to book an appointment"                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTENT DETECTION                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ LLM analyzes message:                                     │   │
│  │ - "booking" → Start/continue booking flow                 │   │
│  │ - "cancel" → Cancel booking (explicit only)               │   │
│  │ - "confirm" → Confirm booking (when awaiting)             │   │
│  │ - "general" → General Q&A                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BOOKING FLOW ACTIVATED                         │
│                  current_mode = 'booking'                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUESTION 1: NAME                              │
│  Bot: "What's the patient's full name?"                          │
│  User: "Sarah Johnson"                                           │
│  ✅ Stored: current_booking['name'] = "Sarah Johnson"            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUESTION 2: EMAIL                             │
│  Bot: "What's your email address?"                               │
│  User: "sarah.johnson@email.com"                                 │
│  ✅ Stored: current_booking['email'] = "sarah.johnson@email.com" │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUESTION 3: PHONE                             │
│  Bot: "What's your phone number? (10 digits)"                    │
│  User: "9876543210"                                              │
│  ✅ Stored: current_booking['phone'] = "9876543210"              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  QUESTION 4: SERVICE TYPE                        │
│  Bot: "Which specialist do you need to see?"                     │
│      Options: GP, Orthopedic, Cardiologist, Dermatologist...    │
│  User: "Cardiologist"                                            │
│  ✅ Stored: current_booking['service_type'] = "Cardiologist"     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUESTION 5: DATE                              │
│  Bot: "What's your preferred date? (YYYY-MM-DD)"                 │
│  User: "2026-01-30"                                              │
│  ✅ Stored: current_booking['date'] = "2026-01-30"               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUESTION 6: TIME                              │
│  Bot: "What time would you prefer? (HH:MM)"                      │
│  User: "14:30" or "2:30 PM"                                      │
│  ✅ Stored: current_booking['time'] = "14:30"                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ALL FIELDS COLLECTED                          │
│                   is_complete() = True                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VALIDATION                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ✓ Email format valid?                                     │   │
│  │ ✓ Phone is 10 digits?                                     │   │
│  │ ✓ Date is future date?                                    │   │
│  │ ✓ Time format valid?                                      │   │
│  │ ✓ Service type matches allowed list?                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
                   ▼                   ▼
              ❌ INVALID          ✅ VALID
                   │                   │
                   │                   │
                   ▼                   ▼
         ┌─────────────────┐  ┌──────────────────────────────────┐
         │ Show Error Msg  │  │      DISPLAY SUMMARY             │
         │ Ask to Correct  │  │  ┌────────────────────────────┐  │
         └─────────────────┘  │  │ 👤 Patient: Sarah Johnson  │  │
                              │  │ 📧 Email: sarah@email.com  │  │
                              │  │ 📱 Phone: 9876543210       │  │
                              │  │ 🎯 Specialty: Cardiologist │  │
                              │  │ 📅 Date: 2026-01-30        │  │
                              │  │ ⏰ Time: 14:30             │  │
                              │  │                            │  │
                              │  │ Is this correct?           │  │
                              │  │ Reply "Yes" to confirm     │  │
                              │  └────────────────────────────┘  │
                              │  awaiting_confirmation = True    │
                              └──────────────┬───────────────────┘
                                             │
                                   ┌─────────┴─────────┐
                                   │                   │
                                   ▼                   ▼
                              "Yes/Confirm"      "No/Cancel"
                                   │                   │
                                   │                   │
                                   ▼                   ▼
                    ┌──────────────────────┐  ┌────────────────┐
                    │  SAVE TO DATABASE    │  │ CANCEL BOOKING │
                    │  ┌────────────────┐  │  │ Reset state    │
                    │  │ 1. Add Customer│  │  │ Return to chat │
                    │  │ 2. Add Booking │  │  └────────────────┘
                    │  │ 3. Get ID      │  │
                    │  └────────────────┘  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  SEND EMAIL          │
                    │  ┌────────────────┐  │
                    │  │ To: User email │  │
                    │  │ Subject: Conf. │  │
                    │  │ Body: Details  │  │
                    │  │ SMTP: Gmail    │  │
                    │  └────────────────┘  │
                    └──────────┬───────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
                     ▼                   ▼
              ✅ EMAIL SENT      ❌ EMAIL FAILED
                     │                   │
                     │                   │
                     ▼                   ▼
         ┌────────────────────┐  ┌──────────────────────┐
         │ ✅ SUCCESS!        │  │ ⚠️ PARTIAL SUCCESS   │
         │ Booking ID: #123   │  │ Booking saved but    │
         │ Email sent to user │  │ email failed         │
         │ View in dashboard  │  │ View in dashboard    │
         └────────────────────┘  └──────────────────────┘
                     │                   │
                     └─────────┬─────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   RESET STATE        │
                    │ - Clear booking data │
                    │ - current_mode = None│
                    │ - awaiting = False   │
                    │ - Ready for next!    │
                    └──────────────────────┘
```

## 🔄 Cancellation Flow

```
ANY POINT IN BOOKING FLOW
         │
         │ User says: "cancel booking"
         │
         ▼
┌─────────────────────┐
│ DETECT CANCEL INTENT│
│ (Explicit only)     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   CANCEL BOOKING    │
│ - Reset all fields  │
│ - Clear mode        │
│ - Show message      │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ RETURN TO GENERAL   │
│ "Booking cancelled. │
│  How can I help?"   │
└─────────────────────┘
```

## 🎯 Priority System

```
MESSAGE RECEIVED
      │
      ▼
┌──────────────────────────────────────┐
│   PRIORITY 1: EXPLICIT CANCELLATION  │
│   "cancel booking" → Cancel          │
└──────────┬───────────────────────────┘
           │ No
           ▼
┌──────────────────────────────────────┐
│   PRIORITY 2: CONFIRMATION           │
│   "yes" + awaiting → Confirm & Save  │
└──────────┬───────────────────────────┘
           │ No
           ▼
┌──────────────────────────────────────┐
│   PRIORITY 3: ACTIVE BOOKING FLOW    │
│   current_booking has data → Continue│
└──────────┬───────────────────────────┘
           │ No
           ▼
┌──────────────────────────────────────┐
│   PRIORITY 4: NEW BOOKING INTENT     │
│   "book appointment" → Start flow    │
└──────────┬───────────────────────────┘
           │ No
           ▼
┌──────────────────────────────────────┐
│   PRIORITY 5: GENERAL QUERY          │
│   Use RAG or LLM for answer          │
└──────────────────────────────────────┘
```

## 📝 Field Extraction Methods

```
USER MESSAGE
      │
      ├──────────────────────────────────┐
      │                                  │
      ▼                                  ▼
┌──────────────┐              ┌──────────────────┐
│ REGEX EXTRACT│              │  LLM EXTRACT     │
│ - Email      │              │ - Natural lang   │
│ - Phone      │              │ - Date parsing   │
│ - Date       │              │ - Context aware  │
│ - Time       │              │ - Flexible       │
└──────┬───────┘              └────────┬─────────┘
       │                               │
       └───────────┬───────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │  MERGE RESULTS   │
         │ Best of both!    │
         └──────────────────┘
```

## 🎨 State Management

```
SESSION STATE
├── chat_logic
│   ├── current_mode: 'booking' | 'general' | None
│   ├── awaiting_confirmation: True | False
│   ├── conversation_history: [last 25 messages]
│   └── booking_flow
│       ├── current_booking: {name, email, phone, ...}
│       ├── required_fields: [6 fields]
│       └── confirmed: True | False
├── messages: [chat history]
└── rag_initialized: True | False
```

---

**Key Points:**
- ✅ Sequential flow ensures all questions asked
- ✅ Priority system prevents accidental cancellation
- ✅ Dual extraction (regex + LLM) for flexibility
- ✅ Validation before confirmation
- ✅ Graceful error handling throughout
