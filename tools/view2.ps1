param([int]$Drag = 0, [int]$DragY = 0, [string]$Out = 'scratch\shot.png',
      [switch]$NoReload)
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public struct RECT { public int L, T, R, B; }
public class Win2 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint x, uint y, int d, int e);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
}
"@
$p = Get-Process | Where-Object { $_.MainWindowTitle -like '*iRacing*' } | Select-Object -First 1
if (-not $p) { Write-Output 'NOWINDOW'; exit 1 }
for ($i = 0; $i -lt 6; $i++) {
  [Win2]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
  Start-Sleep -Milliseconds 400
  if ([Win2]::GetForegroundWindow() -eq $p.MainWindowHandle) { break }
}
if ([Win2]::GetForegroundWindow() -ne $p.MainWindowHandle) { Write-Output 'NOFOCUS' }
$r = New-Object RECT
[Win2]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
$w = $r.R - $r.L; $h = $r.B - $r.T
$cx = $r.L + [int]($w * 0.45); $cy = $r.T + [int]($h * 0.42)
# click once inside the viewer so the 3D pane has keyboard focus
[Win2]::SetCursorPos($cx, $cy); Start-Sleep -Milliseconds 200
[Win2]::mouse_event(0x0002, 0, 0, 0, 0); Start-Sleep -Milliseconds 80
[Win2]::mouse_event(0x0004, 0, 0, 0, 0); Start-Sleep -Milliseconds 400
if (-not $NoReload) {
  [System.Windows.Forms.SendKeys]::SendWait('^r')
  Start-Sleep -Milliseconds 2500
  [System.Windows.Forms.SendKeys]::SendWait('^r')
  Start-Sleep -Milliseconds 4000
}
if ($Drag -ne 0 -or $DragY -ne 0) {
  [Win2]::SetCursorPos($cx, $cy); Start-Sleep -Milliseconds 250
  [Win2]::mouse_event(0x0002, 0, 0, 0, 0); Start-Sleep -Milliseconds 200
  for ($i = 1; $i -le 30; $i++) {
    [Win2]::SetCursorPos(($cx + [int]($Drag * $i / 30)), ($cy + [int]($DragY * $i / 30)))
    Start-Sleep -Milliseconds 20
  }
  Start-Sleep -Milliseconds 150
  [Win2]::mouse_event(0x0004, 0, 0, 0, 0); Start-Sleep -Milliseconds 1200
}
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output ("OK " + $Out + " " + $w + "x" + $h)
