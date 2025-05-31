
# Project Overview

## Name
NetAutoGen (to be changed)

## Purpose
A vendor-agnostic network configuration generator focused on simplicity, speed, and usability.

This tool translates high-level network requirements into valid, ready-to-deploy CLI configuration files for networking devices. The goal is to simplify device setup for both learners and professionals, without requiring deep knowledge of automation tools like Ansible or NetBox.

## Vision
To build a professional, extensible configuration generation system that:
- Accepts structured network inputs (YAML)
- Supports routers, Layer 2 switches, and Layer 3 switches
- Outputs CLI configs using Jinja2 templates
- Can be run from the CLI now, and wrapped in a Web UI/API later

## Core Principles
- **Simple Input → Reliable Output**
- **Clean, testable architecture**
- **Future-proof structure for vendor/device expansion**
- **Separation of logic and presentation (data vs template)**

## Long-Term Goals
- Full topology input → per-device config breakdown
- Multi-vendor support (Cisco first, others later)
- Export for virtual lab platforms (GNS3, EVE-NG)
- Git-compatible config-as-code
- Optional integration with NetBox or live device deployment

---

## Current Phase: Multi-MVP Development

We are tackling the project in three MVPs, one per device type, to modularize development and feature growth.

###  MVP 1: **Cisco Router Config Generator**
- YAML input includes: hostname, interfaces, IPs, default route
- Output: Static routing config in Cisco IOS format
- First full end-to-end test of core system (parser → merge → template → output)

---

###  MVP 2: **Layer 2 Switch Config Generator**
- Focus on:
  - VLAN creation
  - Access/trunk port configs
  - STP options (portfast, bpduguard)
- Will introduce: mode-specific interface logic

---

###  MVP 3: **Layer 3 Switch Config Generator**
- Adds:
  - Switched Virtual Interfaces (SVIs)
  - IP routing + inter-VLAN routing
  - Shared VLAN/IP structures from base input

---

## Tech Stack
- Python 3.x
- PyYAML (input parsing)
- Jinja2 (template rendering)
- CLI interface for now (FastAPI wrapper planned)

---

## Status Summary

- [ ] Project structure and planning 
- [ ] Input field model finalized
- [ ] MVP 1 (Router config)
- [ ] MVP 2 (L2 logic and templates)
- [ ] MVP 3 (SVI + L3 logic)