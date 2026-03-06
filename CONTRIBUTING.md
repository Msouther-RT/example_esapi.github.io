# Contributing to the RT Scripting Hub

Welcome! This guide explains how to add your centre and scripts to the registry.

## Quick overview

1. Fork or clone the repository
2. Create a folder for your centre (if it doesn't exist)
3. Add a script folder with metadata
4. Push your changes — the site rebuilds automatically

## Step-by-step

### 1. Set up your centre folder

If your centre isn't already listed, create a folder under `centres/`. Use a short, lowercase, hyphenated name:

```
centres/your-centre-name/
```

Inside it, create a `centre.json` file:

```json
{
  "name": "Your Hospital Full Name",
  "short_name": "Short Display Name",
  "tps": ["Eclipse"],
  "location": "City, UK"
}
```

The `tps` field is an array — list all TPS systems your centre uses for scripting.

### 2. Add a script

Create a subfolder under `scripts/` with a short descriptive name:

```
centres/your-centre-name/scripts/my-script-name/
```

Inside it, create two files:

**info.json** (required):
```json
{
  "name": "Human Readable Script Name",
  "description": "One or two sentences describing what it does.",
  "tps": "Eclipse",
  "language": "C#",
  "esapi_version": "16.1",
  "status": "in_use",
  "tags": ["dvh", "automation", "plan-evaluation"],
  "last_updated": "2025-01-15",
  "contact_name": "Dr Your Name",
  "contact_email": "your.email@nhs.uk"
}
```

Field reference:
- **name**: Display name for the script
- **description**: Brief summary (shown in the table)
- **tps**: Which TPS this is for (Eclipse, RayStation, Pinnacle, etc.)
- **language**: Programming language (C#, Python, etc.)
- **esapi_version**: ESAPI version tested against (or "N/A" for non-Eclipse)
- **status**: One of `in_use`, `in_development`, `concept`, or `archived`
- **tags**: Array of lowercase keywords for filtering/searching
- **last_updated**: Date of last significant change (YYYY-MM-DD)
- **contact_name**: Person to reach out to about this script
- **contact_email**: Their email address

**README.md** (strongly recommended):
Write a free-form description. We suggest covering:
- What it does
- Why you built it
- How it works (high level)
- Known limitations
- What help you'd welcome (if in development)

You do **not** need to share your actual source code — this is a registry, not a code repository. The point is to let people know what exists so they can reach out to collaborate.

### 3. Status values

| Status | Meaning |
|--------|---------|
| `in_use` | Actively used in your clinical workflow |
| `in_development` | Being built — you may want collaborators |
| `concept` | An idea you'd like to build — looking for interest/help |
| `archived` | No longer maintained but may be useful as reference |

### 4. Submit your changes

**If you have push access**: commit and push to main. The GitHub Action will rebuild the site.

**If you're contributing externally**: open a Pull Request. A maintainer will review and merge it.

### 5. Updating existing scripts

Just edit the relevant `info.json` and/or `README.md` files in your centre's folder and push. The site will rebuild.

## What NOT to include

- **Patient data** of any kind
- **Proprietary Varian/Elekta/etc. code** that you don't have rights to share
- **Executable binaries** — metadata and documentation only

## Building locally

To preview the site locally:

```bash
python3 build.py
# Then open docs/index.html in a browser
```

## Questions?

Open an issue on GitHub or email the maintainers listed in the repository README.