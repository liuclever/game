# 批量删除所有Vue文件中的alert弹窗

$vueFiles = Get-ChildItem -Path "interfaces/client/src" -Filter "*.vue" -Recurse

$totalReplaced = 0

foreach ($file in $vueFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    if ($content -match '\balert\(') {
        # 替换所有alert为console.error或console.log
        $newContent = $content -replace '\balert\(', 'console.error('
        
        if ($newContent -ne $content) {
            Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8 -NoNewline
            $totalReplaced++
            Write-Host "已处理: $($file.Name)"
        }
    }
}

Write-Host "完成！共替换 $totalReplaced 个文件中的alert"
