# Top-down sweep: pitch the camera to the clamp (+600 = top-down), then walk
# around the car in -Step drags, cropping each frame like tools/walk.ps1.
#
#   powershell -ExecutionPolicy Bypass -File tools\walk_top.ps1 -Prefix scratch\t_ -Step 65 -N 8
#
# RSR lesson (2026-09-14): the viewer resets to a front-right 3/4 pose on
# every Ctrl+R, so a reload + this script gives a repeatable top sweep.
param([string]$Prefix = 'scratch\t_', [int]$Step = 65, [int]$N = 8, [int]$DragY = 600)
$view = Join-Path $PSScriptRoot 'view2.ps1'
for ($i = 0; $i -lt $N; $i++) {
  $out = "$Prefix$i.png"
  if ($i -eq 0) { & powershell -ExecutionPolicy Bypass -File $view -NoReload -Out $out -DragY $DragY | Select-String OK }
  else { & powershell -ExecutionPolicy Bypass -File $view -NoReload -Drag $Step -Out $out | Select-String OK }
}
Add-Type -AssemblyName System.Drawing
for ($i = 0; $i -lt $N; $i++) {
  $src = [System.Drawing.Image]::FromFile("$Prefix$i.png")
  $rect = New-Object System.Drawing.Rectangle ([int]($src.Width * 0.03)), ([int]($src.Height * 0.12)), ([int]($src.Width * 0.94)), ([int]($src.Height * 0.76))
  $bmp = New-Object System.Drawing.Bitmap $rect.Width, $rect.Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.DrawImage($src, (New-Object System.Drawing.Rectangle 0, 0, $rect.Width, $rect.Height), $rect, [System.Drawing.GraphicsUnit]::Pixel)
  $bmp.Save("$Prefix$i.jpg", [System.Drawing.Imaging.ImageFormat]::Jpeg)
  $g.Dispose(); $bmp.Dispose(); $src.Dispose()
}
Write-Output "DONE $N frames"
