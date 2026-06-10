$oldPkg = "com.zapotal.zapotalkotlin"
$newPkg = "com.comunidad.zapotal.app"

$baseDir = "app/src"

function Migrate-Files {
    param($sourceRel, $destRel)
    $srcPath = Join-Path $baseDir $sourceRel
    $dstPath = Join-Path $baseDir $destRel
    if (-not (Test-Path $srcPath)) { return }

    New-Item -ItemType Directory -Path $dstPath -Force | Out-Null
    $files = Get-ChildItem -Path $srcPath -Recurse -Filter "*.kt"
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring((Get-Item $srcPath).FullName.Length + 1)
        $newFilePath = Join-Path (Get-Item $dstPath).FullName $relativePath
        $parentDir = Split-Path $newFilePath -Parent
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null

        $content = Get-Content $file.FullName -Raw
        $content = $content -replace "package $oldPkg", "package $newPkg"
        $content = $content -replace "import $oldPkg\.", "import $newPkg."
        $content = $content -replace "\b$oldPkg\.R\b", "$newPkg.R"

        Set-Content -Path $newFilePath -Value $content -NoNewline
    }
}

Migrate-Files "main/java/com/zapotal/zapotalkotlin" "main/java/com/comunidad/zapotal/app"
Migrate-Files "test/java/com/zapotal/zapotalkotlin" "test/java/com/comunidad/zapotal/app"
Migrate-Files "androidTest/java/com/zapotal/zapotalkotlin" "androidTest/java/com/comunidad/zapotal/app"

Remove-Item -Path "$baseDir/main/java/com/zapotal" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$baseDir/test/java/com/zapotal" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$baseDir/androidTest/java/com/zapotal" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Migration complete!"
