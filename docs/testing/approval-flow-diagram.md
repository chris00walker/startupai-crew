# Approval Flow Architecture Diagram

## High-Level Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                         HITL Approval Flow                              │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│   MODAL     │        │  SUPABASE   │        │ PRODUCT APP │
│ Validation  │        │  Database   │        │   Frontend  │
└─────────────┘        └─────────────┘        └─────────────┘

     │                      │                       │
     │  1. Checkpoint       │                       │
     │     Reached          │                       │
     ├─────────────────────►│                       │
     │  Write approval      │                       │
     │  request             │                       │
     │                      │                       │
     │  Terminate           │  2. Realtime Event    │
     │  Container           │  ────────────────────►│
     │  ($0 idle)           │     New approval!     │
     │                      │                       │
     X                      │                       │
  (sleeping)                │                       │
                            │                       │
                            │   3. User Views       │
                            │   ◄───────────────────┤
                            │   GET /api/approvals  │
                            │                       │
                            │   4. User Decides     │
                            │   ◄───────────────────┤
                            │   PATCH /api/         │
                            │   approvals/{id}      │
                            │                       │
                            │   5. Update DB        │
                            │   (approved)          │
                            │                       │
     │  6. Resume Request   │                       │
     │  ◄────────────────────────────────────────────┤
     │  POST /hitl/approve  │                       │
     │                      │                       │
     │  7. Load State       │                       │
     │  ◄───────────────────┤                       │
     │  SELECT state FROM   │                       │
     │  validation_runs     │                       │
     │                      │                       │
     │  8. Continue Flow    │                       │
     │  (with decision)     │                       │
     │                      │                       │
     │  9. Update Progress  │                       │
     │  ─────────────────────►                      │
     │                      │                       │
     │                      │  10. Realtime Update  │
     │                      │  ─────────────────────►
     │                      │      Progress bar     │
     │                      │      updates          │
     │                      │                       │
```

## Detailed API Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                      API Request/Response Flow                          │
└────────────────────────────────────────────────────────────────────────┘

Frontend                    Product App API              Supabase                Modal
   │                              │                         │                      │
   │                              │                         │                      │
   │  1. List Pending Approvals   │                         │                      │
   ├─────────────────────────────►│                         │                      │
   │  GET /api/approvals          │                         │                      │
   │  ?status=pending             │                         │                      │
   │                              │                         │                      │
   │                              │  2. Query DB            │                      │
   │                              ├────────────────────────►│                      │
   │                              │  SELECT * FROM          │                      │
   │                              │  approval_requests      │                      │
   │                              │  WHERE status='pending' │                      │
   │                              │                         │                      │
   │                              │  3. Return Rows         │                      │
   │                              │◄────────────────────────┤                      │
   │                              │  [{approval}, ...]      │                      │
   │                              │                         │                      │
   │  4. Display Approvals        │                         │                      │
   │◄─────────────────────────────┤                         │                      │
   │  200 OK                      │                         │                      │
   │  {approvals: [...]}          │                         │                      │
   │                              │                         │                      │
   │                              │                         │                      │
   │  5. User Clicks Approval     │                         │                      │
   ├─────────────────────────────►│                         │                      │
   │  GET /api/approvals/{id}     │                         │                      │
   │                              │                         │                      │
   │                              │  6. Query Single        │                      │
   │                              ├────────────────────────►│                      │
   │                              │  SELECT * FROM          │                      │
   │                              │  approval_requests      │                      │
   │                              │  WHERE id = '{id}'      │                      │
   │                              │                         │                      │
   │                              │  7. Return Approval     │                      │
   │                              │◄────────────────────────┤                      │
   │                              │  {approval with details}│                      │
   │                              │                         │                      │
   │  8. Show Details             │                         │                      │
   │◄─────────────────────────────┤                         │                      │
   │  200 OK                      │                         │                      │
   │  {id, title, options, ...}   │                         │                      │
   │                              │                         │                      │
   │                              │                         │                      │
   │  9. User Approves            │                         │                      │
   ├─────────────────────────────►│                         │                      │
   │  PATCH /api/approvals/{id}   │                         │                      │
   │  {action: "approve",         │                         │                      │
   │   decision: "segment_1",     │                         │                      │
   │   feedback: "Looks good"}    │                         │                      │
   │                              │                         │                      │
   │                              │ 10. Validate Request    │                      │
   │                              │     (auth, status)      │                      │
   │                              │                         │                      │
   │                              │ 11. Update Approval     │                      │
   │                              ├────────────────────────►│                      │
   │                              │  UPDATE approval_req    │                      │
   │                              │  SET status='approved', │                      │
   │                              │      decision='seg_1',  │                      │
   │                              │      feedback='...',    │                      │
   │                              │      decided_at=NOW()   │                      │
   │                              │                         │                      │
   │                              │ 12. Record History      │                      │
   │                              ├────────────────────────►│                      │
   │                              │  INSERT approval_hist   │                      │
   │                              │  (action='approved')    │                      │
   │                              │                         │                      │
   │                              │ 13. Resume Modal        │                      │
   │                              ├─────────────────────────┼─────────────────────►│
   │                              │                         │  POST /hitl/approve  │
   │                              │                         │  {run_id, checkpoint,│
   │                              │                         │   decision, feedback}│
   │                              │                         │                      │
   │                              │                         │  14. Load State      │
   │                              │                         │◄─────────────────────┤
   │                              │                         │  SELECT state FROM   │
   │                              │                         │  validation_runs     │
   │                              │                         │                      │
   │                              │                         │  15. Resume Flow     │
   │                              │                         │  (continue execution)│
   │                              │                         │                      │
   │                              │ 16. Success Response    │                      │
   │                              │◄────────────────────────┼──────────────────────┤
   │                              │                         │  200 OK              │
   │                              │                         │  {status: "resumed"} │
   │                              │                         │                      │
   │ 17. Success Confirmation     │                         │                      │
   │◄─────────────────────────────┤                         │                      │
   │  200 OK                      │                         │                      │
   │  {success: true,             │                         │                      │
   │   message: "Approved"}       │                         │                      │
   │                              │                         │                      │
   │ 18. Realtime Update          │                         │                      │
   │◄─────────────────────────────┼─────────────────────────┤                      │
   │  (WebSocket)                 │                         │                      │
   │  "approval_requests"         │                         │                      │
   │  UPDATE event                │                         │                      │
   │                              │                         │                      │
   │ 19. UI Updates               │                         │                      │
   │  - Remove from pending       │                         │                      │
   │  - Show success toast        │                         │                      │
   │                              │                         │                      │
```

## Database State Transitions

```
┌────────────────────────────────────────────────────────────────────────┐
│                   approval_requests Table States                        │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│   CREATED   │  ◄─── Modal writes checkpoint
│ status:     │       (or webhook from CrewAI)
│  'pending'  │
└─────────────┘
      │
      │ User views approval
      │
      ▼
┌─────────────┐
│   VIEWED    │  ◄─── Record in approval_history
│ status:     │       (GET /api/approvals/{id})
│  'pending'  │
└─────────────┘
      │
      │ User makes decision
      │
      ▼
┌─────────────┐
│  DECIDED    │  ◄─── PATCH /api/approvals/{id}
│ status:     │       Updates:
│ 'approved'  │       - status
│     OR      │       - decision
│ 'rejected'  │       - human_feedback
└─────────────┘       - decided_by
      │               - decided_at
      │
      │ If approved
      │
      ▼
┌─────────────┐
│  EXECUTED   │  ◄─── Modal resumes
│ status:     │       Record in approval_history
│ 'approved'  │       Validation continues
└─────────────┘
```

## Checkpoint-and-Resume Pattern

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Modal Checkpoint-and-Resume                           │
└────────────────────────────────────────────────────────────────────────┘

BEFORE HITL                  DURING HITL                 AFTER HITL
(Container Running)          (Container Stopped)         (Container Running)

┌─────────────┐             ┌─────────────┐            ┌─────────────┐
│   Phase 1   │             │             │            │   Phase 1   │
│   Running   │             │   Supabase  │            │  Continues  │
│             │             │   Stores:   │            │             │
│   Agents    │             │             │            │   Agents    │
│   Working   │             │   - State   │            │   Resume    │
│             │             │   - Context │            │             │
│   Reached   │             │   - History │            │   With      │
│  Checkpoint │             │   - Pending │            │  Decision   │
│             │             │   Approval  │            │             │
└─────────────┘             └─────────────┘            └─────────────┘
      │                           │                          ▲
      │ 1. Save State             │                          │
      │    to Supabase            │ 2. Wait for              │ 5. Load State
      │                           │    Human                 │    from Supabase
      │                           │    Decision              │
      │                           │                          │ 6. Resume
      │                           │    (hours/days)          │    Execution
      │                           │                          │
      │ 3. Write Approval         │                          │
      │    Request                │ 4. User Approves         │
      │                           │                          │
      │ 4. Terminate              │                          │
      │    Container              │                          │
      ▼                           │                          │
┌─────────────┐             ┌─────────────┐            ┌─────────────┐
│  STOPPED    │             │  WAITING    │            │  RUNNING    │
│  Cost: $0   │             │  Cost: $0   │            │  Cost: $/s  │
└─────────────┘             └─────────────┘            └─────────────┘
```

## Cost Savings

```
Traditional Always-On Container:
├─ Running Time: 24 hours/day
├─ Actual Work: 2 hours validation + 22 hours HITL
└─ Cost: $X * 24 hours = $24X

Modal Checkpoint-and-Resume:
├─ Running Time: 2 hours validation only
├─ HITL Time: 0 hours (container stopped)
└─ Cost: $X * 2 hours = $2X

Savings: 92% reduction in compute costs
```

---

**Last Updated**: 2026-01-12
**Maintainer**: Chris Walker
