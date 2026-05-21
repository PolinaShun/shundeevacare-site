# Test Protocol: ShundeevaCare Site

This document outlines the mandatory verification scenarios for the project.

## 1. Visual Verification
- [ ] Mobile Responsiveness: Check the page on common screen widths.
- [ ] Layout Integrity: Ensure no elements are overlapping or broken.
- [ ] Images: All images must load correctly.

## 2. Functional Verification
- [ ] Links: All modified or added links must be RELATIVE and functional.
- [ ] Forms: If any forms exist, verify they submit correctly (or mock the submission).
- [ ] Navigation: Menu and footer links should work.

## 3. Deployment Readiness
- [ ] HTML Validation: No broken tags or critical syntax errors.
- [ ] Console Errors: No JavaScript errors in the browser console.
- [ ] File Paths: Ensure all assets (CSS, JS, Images) use correct relative paths.

## Procedure
1. Perform changes.
2. Run local verification.
3. **Invoke Sub-agent:** Call a testing sub-agent to run through this checklist before final delivery.
