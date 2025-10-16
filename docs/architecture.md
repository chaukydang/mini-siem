# Mini-SIEM — Step 1 (Collector & Storage)


## Common Schema (required)
- ts (ISO8601, UTC), source, host, ip, endpoint, method, status_code, resp_time_ms, ua, action_type


## Optional
- user_id, session_id, bytes_in, bytes_out, referrer, query_params, error, raw


## Mapping Notes
- Nginx: $remote_addr -> ip, $request -> method+endpoint, $status -> status_code, $http_user_agent -> ua
- App JSON: map 1:1 where possible
- DB audit: action_type = "db_query", put statement/params into query_params (mask PII)
