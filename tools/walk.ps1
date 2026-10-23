# Walk the car viewer camera around the car and crop every frame to the 3D pane.
#
#   powershell -ExecutionPolicy Bypass -File tools\walk.ps1 -Prefix scratch\w_ -Step 65 -N 12 [-Reload] [-DragY -600]
#
# Frame 0 is captured where the camera is (after -DragY, e.g. -600 = level,
# +600 = top-down); each following frame first drags -Step px horizontally.
# Writes <Prefix><i>.png (window capture) and <Prefix><i>.jpg (the 3D pane,
# cropped PROPORTIONALLY - the iRacing window changes size).  Then tile them
# with tools/contact_sheet.py.  F4 lesson (2026-09-14): with a 1728-px-wide
# window 65 px is ~30 deg on average but non-linear - sweep 12 frames and
# pick, never assume a pose.  Keep -N so the whole call finishes in ~60 s
# (Desktop Commander's bridge limit); split longer walks.
param([string]$Prefix = 'scratch\w_', [int]$Step = 65, [int]$N = 12, [switch]$Reload, [int]$DragY = 0)
$view = Join-Path $PSScriptRoot 'view2.ps1'
for ($i = 0; $i -lt $N; $i++) {
  $out = "$Prefix$i.png"
  if ($i -eq 0) {
    if ($Reload) { & powershell -ExecutionPolicy Bypass -File $view -Out $out -DragY $DragY | Select-String OK }
    else { & powershell -ExecutionPolicy Bypass -File $view -NoReload -Out $out -DragY $DragY | Select-String OK }
  } else {
    & powershell -ExecutionPolicy Bypass -File $view -NoReload -Drag $Step -Out $out | Select-String OK
  }
}
Add-Type -AssemblyName System.Drawing
for ($i = 0; $i -lt $N; $i++) {
  $src = [System.Drawing.Image]::FromFile("$Prefix$i.png")
  $rect = New-Object System.Drawing.Rectangle ([int]($src.Width * 0.03)), ([int]($src.Height * 0.18)), ([int]($src.Width * 0.94)), ([int]($src.Height * 0.69))
  $bmp = New-Object System.Drawing.Bitmap $rect.Width, $rect.Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.DrawImage($src, (New-Object System.Drawing.Rectangle 0, 0, $rect.Width, $rect.Height), $rect, [System.Drawing.GraphicsUnit]::Pixel)
  $bmp.Save("$Prefix$i.jpg", [System.Drawing.Imaging.ImageFormat]::Jpeg)
  $g.Dispose(); $bmp.Dispose(); $src.Dispose()
}
Write-Output "DONE $N frames"
