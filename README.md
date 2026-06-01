# Quotation Software 

## Overview
This is a professional Quotation management software designed to streamline the process of generating financial documents and managing client relationships. It includes a modern dashboard, comprehensive document generation tools, and integrated marketing bots.

## Features
- **Document Generation**: Easily create and export:
  - Quotations
  - Tax Invoices
  - Commercial Invoices
  - Delivery Challans (with auto-generated signature notes)
- **Dashboard & Analytics**: 
  - Real-time sales performance graphs.
  - Monthly sales summaries.
  - Recent activity tracking.
- **Client Management**:
  - Detailed client history and ledgers.
  - Quick access to client summaries.
- **Marketing Automation**:
  - **WhatsApp Bot**: Send bulk messages with attachments for marketing campaigns.
  - **Instagram Lead Miner**: Automated DM bot to reach potential clients.
- **Security & User Management**:
  - Secure Login System with "Remember Me" functionality.
  - **Enhanced**: Full-screen login and setup interface.
  - **New**: Profile picture upload for user accounts.
  - Password recovery via security question.
  - Role-based access (Admin/User).
- **Customization**:
  - Theme Manager with multiple skins (Cosmo, Dark, etc.).
  - Custom header/footer and logo alignment.
- **PDF Generation**: High-quality PDF output using ReportLab.

## Technologies Used
- **Python**: Core logic.
- **Tkinter / ttkbootstrap**: Graphical User Interface.
- **SQLite / SQL Server**: Database management.
- **Selenium**: Automation for WhatsApp and Instagram bots.
- **ReportLab**: PDF generation.
- **Matplotlib**: Data visualization.

## How to Use
1. **Installation**: Ensure Python is installed along with the required libraries (selenium, pandas, reportlab, ttkbootstrap, etc.).
2. **Launch**: Run the `quotation.py` file to start the application.
   ```bash
   python quotation.py
   ```
3. **Setup**: On the first run, you will be prompted to set up an Admin profile.
4. **Operation**: Use the dashboard to navigate between creating quotations, invoices, and managing marketing tools.

## Public Downloads While Source Stays Private
Use this repository as private source code, and publish installers to a separate public repository:

1. Create a public repository (example: `your-org/Quotation-Software-Downloads`).
2. In this private repository, add:
   - Repository variable: `PUBLIC_DOWNLOADS_REPO` = `owner/public-download-repo`
   - Repository secret: `PUBLIC_REPO_TOKEN` = GitHub PAT with `repo` access to the public downloads repository
3. Push a version tag (for example `v5.3.0`) to trigger the release workflow.
4. The workflow uploads Windows and macOS binaries to the public repository release with the same tag.
5. Use website button links in this format:
   - `https://github.com/<owner>/<public-download-repo>/releases/latest/download/QuotationGenerator_Setup_v5.2.exe`
   - `https://github.com/<owner>/<public-download-repo>/releases/latest/download/QuotationGenerator-macOS.zip`

Do not use GitHub Actions artifact URLs for end-user downloads, because they require authenticated access.

---
We will improve it further.
