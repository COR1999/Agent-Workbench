## Environment

This machine is Windows 11 with Git Bash.

- **Git Bash rewrites POSIX-looking arguments into Windows paths** before handing
  them to native executables. `--title '/admin/customers is slow'` arrives as
  `C:/Program Files/Git/admin/customers is slow`. This has already corrupted a
  real GitHub issue title. Prefix with `MSYS_NO_PATHCONV=1`, or use PowerShell,
  for any command whose arguments contain a leading slash.
- **There is no Docker on this machine.** Anything requiring a container, a local
  Postgres, or `supabase start` runs in CI only. Never report such a step as
  verified locally.
