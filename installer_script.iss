[Setup]
AppName=SecureMessenger
AppVersion=1.0.0
DefaultDirName={userappdata}\SecureMessenger
DefaultGroupName=SecureMessenger
PrivilegesRequired=lowest
OutputBaseFilename=SecureMessenger-Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile=resources\icons\app_icon.ico

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SecureMessenger"; Filename: "{app}\SecureMessenger.exe"
Name: "{userdesktop}\SecureMessenger"; Filename: "{app}\SecureMessenger.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\SecureMessenger.exe"; Description: "{cm:LaunchProgram,SecureMessenger}"; Flags: nowait postinstall skipifsilent