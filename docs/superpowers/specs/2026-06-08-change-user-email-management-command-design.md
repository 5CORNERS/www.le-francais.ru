# Spec: change_user_email Management Command

## Overview
A Django management command for the `custom_user` app to securely and programmatically replace a user's email address in django-allauth, mark it verified and primary, sync the User model, and delete the old email address.

## Objectives
- Allow administrators to swap a user's email via command-line interface.
- Keep `django-allauth`'s `EmailAddress` state and Django's `User.email` perfectly synchronized.
- Ensure safety by using database transactions.
- Prevent typos/errors with interactive confirmation, while supporting a `--no-input` option for automated execution (e.g. scripts or CI).

---

## Technical Design

### 1. File Location & CLI Invocation
- **Path**: `custom_user/management/commands/change_user_email.py`
- **Command Signature**:
  ```powershell
  python manage.py change_user_email <user_identifier> <new_email> [--no-input]
  ```

### 2. Argument Definitions
- **`user_identifier`** (string, required): Look up target user. Supports user ID, username, or current primary email.
- **`new_email`** (string, required): The target email address to set.
- **`--no-input`** (flag, optional): Disables interactive confirmation prompts.

### 3. Step-by-Step Execution Sequence

1. **User Resolution**:
   - If input is numeric, attempt search by ID: `User.objects.filter(pk=int(user_identifier)).first()`.
   - If not found or not numeric, attempt search by username: `User.objects.filter(username__iexact=user_identifier).first()`.
   - If not found, attempt search by current email: `User.objects.filter(email__iexact=user_identifier).first()`.
   - If still not found, print error and exit with code `1`.

2. **Validation**:
   - Normalize the new email: `<new_email>.strip().lower()`.
   - If user's current email already matches normalized `new_email`, exit early with success.
   - Verify if `new_email` is already registered to *any other user* using `EmailAddress.objects.filter(email__iexact=new_email).exclude(user=user)`. If it is, fail with a clear message and exit with code `1`.

3. **Interactive Confirmation**:
   - Unless `--no-input` is passed, display:
     ```
     You are about to change the email for:
       User: <username> (ID: <id>)
       Current Primary Email: <current_email>
       New Primary Email: <new_email>

     WARNING: This will:
       - Associate the new email address with this user.
       - Mark it as VERIFIED.
       - Set it as the PRIMARY email address (synchronizing with User.email).
       - DELETE the old email address(es) associated with this user.

     Are you sure you want to proceed? [y/N]: 
     ```
   - If user responds with anything other than `y`/`yes` (case-insensitive), abort execution.

4. **Atomic Transaction (`transaction.atomic`)**:
   - Retrieve all current `EmailAddress` records for the user excluding the `new_email` (these are scheduled for deletion).
   - Fetch or create the `EmailAddress` instance for `new_email`.
   - Mark the new email record as verified (`verified = True`) and save.
   - Call `new_email_obj.set_as_primary()` which updates `user.email`, unsets the primary flag on other emails, and saves both records.
   - Delete all old collected `EmailAddress` records.

5. **Completion**:
   - Print success message showing old and new email addresses.

---

## Verification & Testing Plan

### 1. Unit/Integration Tests
We will add `ChangeUserEmailCommandTestCase` to `custom_user/tests.py` testing the following:
- **Test Success Path (Interactive Prompt Skipped via `--no-input`)**: Verifies email address is correctly added, verified, set as primary, user email updated, and old emails deleted.
- **Test User Resolution**: Ensures finding user by ID, username, and email works correctly.
- **Test Duplication Check**: Verifies attempting to assign an email already used by another user fails and aborts.
- **Test Abort Path**: Ensures that if interactive confirmation is rejected, no changes are written.

### 2. Manual Verification
Run the command manually with test inputs:
```powershell
python manage.py change_user_email some_test_user new_verified_email@example.com
```
Verify stdout output and confirm database state.
