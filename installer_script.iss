[Setup]
AppName=Crossword Generator AI
AppVersion={#MyAppVersion}
DefaultDirName={pf}\CrosswordGenerator
DefaultGroupName=CrosswordGenerator
OutputDir=Output
OutputBaseFilename=CrosswordGeneratorSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\CrosswordGenerator"; Filename: "{app}\main\main.exe"