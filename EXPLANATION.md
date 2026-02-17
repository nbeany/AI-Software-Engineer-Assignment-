# EXPLANATION

## What was the bug?

In `app/http_client.py`, the token-refresh condition inside `request()` only triggered a refresh when the token was `None`/falsy **or** when it was an `OAuth2Token` instance that had expired. It never refreshed when the token was a **non-empty dict** — a type the class explicitly accepts via its `Union[OAuth2Token, Dict[str, Any], None]` annotation.

## Why did it happen?

The condition was:

```python
if not self.oauth2_token or (
    isinstance(self.oauth2_token, OAuth2Token) and self.oauth2_token.expired
):
```

A non-empty dict (e.g. `{"access_token": "stale", "expires_at": 0}`) evaluates as truthy, so `not self.oauth2_token` is `False`. The second clause also short-circuits to `False` because the dict is not an `OAuth2Token` instance. The refresh was skipped entirely, and the subsequent `isinstance` guard meant no `Authorization` header was ever set either.

## Why does your fix actually solve it?

The updated condition is:

```python
if not self.oauth2_token or not isinstance(self.oauth2_token, OAuth2Token) or self.oauth2_token.expired:
```

This adds `not isinstance(self.oauth2_token, OAuth2Token)` as an explicit branch. Any token value that is not a proper `OAuth2Token` — regardless of its truthiness or contents — now triggers a refresh, after which the token is a valid `OAuth2Token` and the `Authorization` header is set correctly.

## One realistic edge case the tests still don't cover

An `OAuth2Token` whose `expires_at` is exactly equal to the current Unix timestamp (i.e. it expires *right now*). The `expired` property uses `>=`, so it is treated as expired and a refresh is triggered — but between the `expired` check and the `refresh_oauth2()` call the clock could tick forward, meaning the refreshed token could theoretically also be evaluated as expired on a very slow system. This race condition is not tested.

