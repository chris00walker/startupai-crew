# Production Cutover Checklist

**Date**: 2026-01-08
**Migration**: CrewAI AMP → Modal Serverless
**Reference**: [ADR-002](../adr/002-modal-serverless-migration.md)

## Pre-Cutover Verification

### 1. Tests ✅
- [x] All 118 Modal-specific tests passing
- [x] Integration tests verified
- [x] E2E tests verified

### 2. Modal Dev Environment ✅
- [x] Modal app deployed to dev: `modal deploy src/modal_app/app.py --env dev`
- [x] Health endpoint responding
- [x] Dev URL: `https://chris00walker-dev--startupai-validation-fastapi-app.modal.run`

### 3. Supabase Migration ✅
- [x] Migration `add_modal_columns_to_validation_runs` applied (2026-01-08)
- [x] Migration `enable_rls_modal_tables` applied (2026-01-08)

**Added columns**: `run_id`, `session_id`, `provider`, `phase_name`, `inputs`, `outputs`, `progress`, `hitl_checkpoint`, `error`

**RLS policies enabled on**:
- `validation_runs` - users see own runs, service role full access
- `validation_progress` - users see own progress, service role full access
- `hitl_requests` - users see/update own requests, service role full access
- `public_activity_log` - public read access, service role full access

### 4. Enable Realtime (Optional)
For real-time progress updates:
```sql
ALTER PUBLICATION supabase_realtime ADD TABLE validation_progress;
ALTER PUBLICATION supabase_realtime ADD TABLE hitl_requests;
```

---

## Production Deployment

### 5. Deploy Modal to Production
```bash
cd /home/chris/projects/startupai-crew
modal deploy src/modal_app/app.py --env main
```

**Verify**:
```bash
curl https://chris00walker--startupai-validation-fastapi-app.modal.run/health
# Expected: {"status":"healthy","service":"startupai-validation"}
```

### 6. Product App (app.startupai.site)
Already updated with Modal support. Deploy via Netlify:
```bash
cd /home/chris/projects/app.startupai.site/frontend
netlify deploy --prod
```

Or trigger via Netlify dashboard: https://app.netlify.com/

### 7. Marketing Site (startupai.site)
Already updated with live data APIs. Deploy via Netlify:
```bash
cd /home/chris/projects/startupai.site
netlify deploy --prod
```

---

## Post-Cutover Verification

### 8. E2E Smoke Test
1. Go to https://app.startupai.site
2. Complete onboarding flow
3. Verify validation kicks off (check Supabase `validation_runs` table)
4. Verify progress updates appear in UI
5. Verify HITL checkpoint appears when reached

### 9. Marketing Site Verification
1. Go to https://startupai.site/about
2. Verify "Live data" indicator appears
3. Verify metrics update from API

### 10. Monitoring
- Modal Dashboard: https://modal.com/apps/startupai-validation
- Supabase Logs: https://supabase.com/dashboard/project/eqxropalhxjeyvfcoyxg/logs
- Netlify Functions Logs: https://app.netlify.com/sites/startupai/functions

---

## Rollback Plan

If issues occur, rollback to AMP:

1. **Product App**: Revert `src/app/api/analyze/route.ts` to use AMP endpoint
2. **Environment**: Set `CREWAI_USE_MODAL=false` in Netlify env vars
3. **Verify**: AMP still operational at existing URLs

AMP endpoints (deprecated but still deployed):
- Crew 1: `https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com`
- Crew 2: `https://startupai-3135e285-c0e6-4451-b7b6-d4a061ac44-e2dea8c9.crewai.com`
- Crew 3: `https://startupai-7da95dc8-7bb5-4c90-925b-2861fa9cba-46bd3a78.crewai.com`

---

## Environment Variables

### Modal Secrets (Already configured)
```bash
modal secret list
# startupai-secrets should contain:
# - OPENAI_API_KEY
# - TAVILY_API_KEY
# - SUPABASE_URL
# - SUPABASE_KEY
# - NETLIFY_ACCESS_TOKEN
```

### Product App (Netlify)
```env
MODAL_WEBHOOK_TOKEN=startupai-modal-webhook-2024
CREWAI_USE_MODAL=true  # Optional: for gradual rollout
```

---

## Completion Checklist

- [ ] Supabase migration applied
- [ ] Modal deployed to production (main env)
- [ ] Product app deployed to Netlify
- [ ] Marketing site deployed to Netlify
- [ ] E2E smoke test passed
- [ ] Marketing site showing live data
- [ ] No errors in Modal/Supabase logs

**Cutover Complete**: ______ (date/time)
**Verified By**: ______
