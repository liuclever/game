# 批量删除所有Vue文件中的alert弹窗，替换为console.log或console.error

$files = Get-ChildItem -Path "interfaces/client/src" -Filter "*.vue" -Recurse | Where-Object {
    $content = Get-Content $_.FullName -Raw
    $content -match '\balert\('
}

$totalFiles = $files.Count
$currentFile = 0

Write-Host "找到 $totalFiles 个包含alert的文件"

foreach ($file in $files) {
    $currentFile++
    Write-Host "[$currentFile/$totalFiles] 处理: $($file.Name)"
    
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # 替换alert为console.log或console.error
    # 对于错误信息使用console.error
    $content = $content -replace '\balert\(([^)]*(?:失败|错误|不足|无法|缺少)[^)]*)\)', 'console.error($1)'
    # 对于成功信息使用console.log
    $content = $content -replace '\balert\(([^)]*)\)', 'console.log($1)'
    
    Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
}

Write-Host "完成！共处理 $totalFiles 个文件"
