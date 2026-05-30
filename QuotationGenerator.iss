; ============================================================
; Inno Setup Script for Quotation Generator
; Professional Installer for Orient Marketing Software
; ============================================================

#define MyAppName "Quotation Generator"
#define MyAppVersion "5.2"
#define MyAppPublisher "Orient Marketing"
#define MyAppExeName "QuotationGenerator.exe"
#define MyAppIcon "logo.ico"

[Setup]
; App identity
AppId={{B8F3A1C2-4D5E-6F7A-8B9C-0D1E2F3A4B5C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output settings
OutputDir=installer_output
OutputBaseFilename=QuotationGenerator_Setup_v{#MyAppVersion}
SetupIconFile=logo.ico
Compression=lzma2/ultra64
SolidCompression=yes

; Visual settings
WizardStyle=modern
WizardSizePercent=120

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Uninstall
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Misc
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application and all PyInstaller output
Source: "dist\QuotationGenerator\QuotationGenerator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\QuotationGenerator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Database files (empty templates — user data will be created at runtime)
; NOTE: We do NOT bundle .db files — they are created fresh by the app on first run

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up auto-generated files on uninstall
Type: filesandordirs; Name: "{app}\db"
Type: files; Name: "{app}\*.log"
Type: dirifempty; Name: "{app}"
