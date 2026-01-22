# 🧪 Testing Checklist - AI Booking Assistant

## Pre-Testing Setup

- [ ] Application is running (`streamlit run app/main.py`)
- [ ] Browser opened to http://localhost:8501
- [ ] `.env` file has all required API keys
- [ ] Database file exists or will be created

---

## ✅ Test Suite 1: Basic Booking Flow

### Test 1.1: Complete Booking (Happy Path)
**Steps:**
1. Type: "I want to book an appointment"
2. Answer: "John Smith" (name)
3. Answer: "john.smith@email.com" (email)
4. Answer: "1234567890" (phone)
5. Answer: "Cardiologist" (service)
6. Answer: "2026-02-15" (date)
7. Answer: "14:30" (time)
8. Type: "Yes" (confirm)

**Expected Results:**
- [ ] All 6 questions asked in order
- [ ] No questions skipped
- [ ] Summary displayed correctly
- [ ] Booking saved with ID
- [ ] Email confirmation message shown
- [ ] Success message displayed

**Actual Result:** ________________

---

### Test 1.2: Booking with Multi-Field Input
**Steps:**
1. Type: "Book appointment for Sarah Johnson, email sarah@test.com, phone 9876543210"
2. Answer remaining questions as prompted

**Expected Results:**
- [ ] Name, email, and phone extracted from first message
- [ ] Only asks for missing fields (service, date, time)
- [ ] Booking completes successfully

**Actual Result:** ________________

---

### Test 1.3: Booking Cancellation
**Steps:**
1. Type: "I want to book an appointment"
2. Answer first 2-3 questions
3. Type: "cancel booking"

**Expected Results:**
- [ ] Booking cancelled immediately
- [ ] Message: "Booking cancelled. Would you like to start over..."
- [ ] Can start new booking or ask general questions
- [ ] Previous booking data cleared

**Actual Result:** ________________

---

## ✅ Test Suite 2: Validation

### Test 2.1: Invalid Email
**Steps:**
1. Start booking flow
2. Provide invalid email: "notanemail"

**Expected Results:**
- [ ] System accepts input initially
- [ ] Validation fails at summary stage
- [ ] Error message shown
- [ ] Asks to correct email

**Actual Result:** ________________

---

### Test 2.2: Invalid Phone
**Steps:**
1. Start booking flow
2. Provide invalid phone: "123" (too short)

**Expected Results:**
- [ ] Validation fails
- [ ] Error: "Phone number must be 10 digits"
- [ ] Asks for correction

**Actual Result:** ________________

---

### Test 2.3: Past Date
**Steps:**
1. Start booking flow
2. Provide past date: "2020-01-01"

**Expected Results:**
- [ ] Validation fails
- [ ] Error: "Booking date cannot be in the past"
- [ ] Asks for new date

**Actual Result:** ________________

---

### Test 2.4: Invalid Time Format
**Steps:**
1. Start booking flow
2. Provide invalid time: "25:00" or "abc"

**Expected Results:**
- [ ] Validation fails
- [ ] Error: "Invalid time format"
- [ ] Asks for correction

**Actual Result:** ________________

---

## ✅ Test Suite 3: Intent Detection

### Test 3.1: Normal Responses Not Treated as Cancel
**Steps:**
1. Start booking flow
2. When asked for name, type: "Michael"
3. Continue with other fields

**Expected Results:**
- [ ] "Michael" stored as name
- [ ] NOT treated as cancellation
- [ ] Flow continues normally

**Actual Result:** ________________

---

### Test 3.2: "Yes" During Booking
**Steps:**
1. Start booking flow
2. When asked for name, type: "Yes Smith"

**Expected Results:**
- [ ] "Yes Smith" stored as name
- [ ] NOT treated as confirmation
- [ ] Flow continues to next question

**Actual Result:** ________________

---

### Test 3.3: Explicit Cancel Phrases
**Test each phrase:**
- [ ] "cancel" → Cancels booking
- [ ] "cancel booking" → Cancels booking
- [ ] "stop booking" → Cancels booking
- [ ] "cancel appointment" → Cancels booking

**Actual Results:** ________________

---

## ✅ Test Suite 4: Email Functionality

### Test 4.1: Email Sent Successfully
**Steps:**
1. Complete a booking with valid email
2. Check console output for SMTP logs

**Expected Results:**
- [ ] "✅ SMTP Login successful" in console
- [ ] "✅ Message sent" in console
- [ ] Success message in chat
- [ ] Email received (check inbox)

**Actual Result:** ________________

---

### Test 4.2: Email Failure Handling
**Steps:**
1. Temporarily set invalid email credentials in `.env`
2. Complete a booking

**Expected Results:**
- [ ] Booking still saves to database
- [ ] Warning message shown
- [ ] "Email could not be sent, but booking was saved"
- [ ] Booking visible in admin dashboard

**Actual Result:** ________________

---

## ✅ Test Suite 5: Admin Dashboard

### Test 5.1: Login
**Steps:**
1. Click "📊 Admin Dashboard" tab
2. Enter username: "Arjun"
3. Enter password: "arjun123"
4. Click Login

**Expected Results:**
- [ ] Login successful
- [ ] Dashboard displays
- [ ] Can see bookings table

**Actual Result:** ________________

---

### Test 5.2: View Bookings
**Steps:**
1. Login to admin dashboard
2. Check "📋 Appointments" tab

**Expected Results:**
- [ ] All bookings displayed
- [ ] Correct patient names
- [ ] Correct dates and times
- [ ] Status shown (Pending/Confirmed/etc.)
- [ ] Metrics displayed (Total, Pending, Confirmed)

**Actual Result:** ________________

---

### Test 5.3: Edit Booking Status
**Steps:**
1. Login to admin dashboard
2. Click on a status dropdown
3. Change from "Pending" to "Confirmed"

**Expected Results:**
- [ ] Status updates immediately
- [ ] Toast notification shown
- [ ] Change persists after refresh

**Actual Result:** ________________

---

### Test 5.4: View Patients
**Steps:**
1. Login to admin dashboard
2. Click "👥 Patients" tab

**Expected Results:**
- [ ] All customers displayed
- [ ] Shows customer_id, name, email, phone
- [ ] Data matches bookings

**Actual Result:** ________________

---

## ✅ Test Suite 6: RAG Functionality

### Test 6.1: Upload PDF
**Steps:**
1. Click "📄 Upload Documents" in sidebar
2. Select a PDF file
3. Click "🚀 Process PDFs"

**Expected Results:**
- [ ] Processing spinner shows
- [ ] Success message: "Processed X files, created Y chunks"
- [ ] RAG status changes to "✅"

**Actual Result:** ________________

---

### Test 6.2: Query PDF
**Steps:**
1. After uploading PDF
2. Ask a question about the PDF content

**Expected Results:**
- [ ] Answer retrieved from PDF
- [ ] Relevant information shown
- [ ] Source context included

**Actual Result:** ________________

---

### Test 6.3: Clear PDF Database
**Steps:**
1. After uploading PDFs
2. Click "🗑️ Forget PDF Database"

**Expected Results:**
- [ ] Success message shown
- [ ] RAG status changes to "⏳"
- [ ] Can upload new PDFs

**Actual Result:** ________________

---

## ✅ Test Suite 7: General Chat

### Test 7.1: General Questions
**Steps:**
1. Ask: "What services do you offer?"
2. Ask: "What are your hours?"

**Expected Results:**
- [ ] Receives general response
- [ ] Does NOT start booking flow
- [ ] Can ask follow-up questions

**Actual Result:** ________________

---

### Test 7.2: Switch from Chat to Booking
**Steps:**
1. Ask general questions
2. Then say: "I want to book an appointment"

**Expected Results:**
- [ ] Switches to booking mode
- [ ] Starts asking booking questions
- [ ] Previous chat context maintained

**Actual Result:** ________________

---

## ✅ Test Suite 8: Edge Cases

### Test 8.1: Empty Input
**Steps:**
1. Start booking
2. Press Enter without typing anything

**Expected Results:**
- [ ] No error
- [ ] Asks question again or handles gracefully

**Actual Result:** ________________

---

### Test 8.2: Very Long Input
**Steps:**
1. Type a very long message (500+ characters)

**Expected Results:**
- [ ] System handles without error
- [ ] Extracts relevant information
- [ ] Responds appropriately

**Actual Result:** ________________

---

### Test 8.3: Special Characters
**Steps:**
1. Use special characters in name: "O'Brien"
2. Use special characters in email: "test+tag@email.com"

**Expected Results:**
- [ ] Accepts special characters
- [ ] Stores correctly
- [ ] No errors

**Actual Result:** ________________

---

## ✅ Test Suite 9: Session Management

### Test 9.1: Chat History
**Steps:**
1. Have a long conversation (30+ messages)
2. Check that old messages are removed

**Expected Results:**
- [ ] Only last 25 messages kept
- [ ] Welcome message retained
- [ ] No memory issues

**Actual Result:** ________________

---

### Test 9.2: Clear Chat History
**Steps:**
1. Have a conversation
2. Click "🧹 Clear Chat History" in sidebar

**Expected Results:**
- [ ] All messages cleared except welcome
- [ ] Can start fresh conversation
- [ ] No errors

**Actual Result:** ________________

---

### Test 9.3: Reset & Reload Config
**Steps:**
1. Click "🔄 Reset & Reload Config"

**Expected Results:**
- [ ] All session state cleared
- [ ] Configuration reloaded
- [ ] App reinitializes
- [ ] Welcome message shown

**Actual Result:** ________________

---

## ✅ Test Suite 10: Database

### Test 10.1: Database Creation
**Steps:**
1. Delete `amrita_bookings.db` if exists
2. Start application
3. Complete a booking

**Expected Results:**
- [ ] Database file created automatically
- [ ] Tables created (customers, bookings)
- [ ] Booking saved successfully

**Actual Result:** ________________

---

### Test 10.2: Duplicate Customer
**Steps:**
1. Complete booking with email: "test@email.com"
2. Complete another booking with same email

**Expected Results:**
- [ ] Uses existing customer record
- [ ] Creates new booking record
- [ ] No duplicate customer entries

**Actual Result:** ________________

---

## 📊 Test Results Summary

### Total Tests: 35

**Passed:** _____ / 35
**Failed:** _____ / 35
**Skipped:** _____ / 35

### Critical Issues Found:
1. ________________________________
2. ________________________________
3. ________________________________

### Minor Issues Found:
1. ________________________________
2. ________________________________
3. ________________________________

### Recommendations:
1. ________________________________
2. ________________________________
3. ________________________________

---

## ✅ Final Verification

Before deployment, ensure:

- [ ] All critical tests pass
- [ ] No auto-cancellation issues
- [ ] All questions asked in order
- [ ] Email functionality works
- [ ] Admin dashboard functional
- [ ] Database operations correct
- [ ] UI/UX is professional
- [ ] Error handling is graceful
- [ ] Documentation is complete

---

## 🎯 Sign-off

**Tested By:** ________________
**Date:** ________________
**Status:** ☐ PASS  ☐ FAIL  ☐ NEEDS WORK

**Notes:**
_________________________________________________
_________________________________________________
_________________________________________________

---

**Ready for Deployment:** ☐ YES  ☐ NO

**If NO, what needs to be fixed:**
_________________________________________________
_________________________________________________
_________________________________________________
