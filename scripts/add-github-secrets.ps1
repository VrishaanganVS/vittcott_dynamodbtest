# GitHub Secrets Setup Helper
# This script helps you add secrets to GitHub repository

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     GitHub Secrets Setup Helper                           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Repository info
$owner = "VrishaanganVS"
$repo = "vittcott_dynamodbtest"
$secretsUrl = "https://github.com/$owner/$repo/settings/secrets/actions"

Write-Host "🔐 You need to add 5 secrets to GitHub`n" -ForegroundColor Yellow

# Check if GitHub CLI is installed
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if ($ghInstalled) {
    Write-Host "✅ GitHub CLI detected! I can help you add secrets automatically.`n" -ForegroundColor Green
    
    Write-Host "Do you want to add secrets now? (y/n): " -NoNewline -ForegroundColor Cyan
    $response = Read-Host
    
    if ($response -eq 'y') {
        Write-Host "`nEnter your API keys (press Enter to skip):`n" -ForegroundColor Yellow
        
        # GEMINI_API_KEY
        Write-Host "GEMINI_API_KEY: " -NoNewline -ForegroundColor Cyan
        $gemini = Read-Host -AsSecureString
        if ($gemini.Length -gt 0) {
            $geminiPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($gemini))
            gh secret set GEMINI_API_KEY --body $geminiPlain --repo "$owner/$repo"
            Write-Host "  ✓ Added GEMINI_API_KEY" -ForegroundColor Green
        }
        
        # FINANCEHUB_API_KEY
        Write-Host "FINANCEHUB_API_KEY: " -NoNewline -ForegroundColor Cyan
        $finnhub = Read-Host -AsSecureString
        if ($finnhub.Length -gt 0) {
            $finnhubPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($finnhub))
            gh secret set FINANCEHUB_API_KEY --body $finnhubPlain --repo "$owner/$repo"
            Write-Host "  ✓ Added FINANCEHUB_API_KEY" -ForegroundColor Green
        }
        
        # AWS_ACCESS_KEY_ID
        Write-Host "AWS_ACCESS_KEY_ID: " -NoNewline -ForegroundColor Cyan
        $awsKey = Read-Host -AsSecureString
        if ($awsKey.Length -gt 0) {
            $awsKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($awsKey))
            gh secret set AWS_ACCESS_KEY_ID --body $awsKeyPlain --repo "$owner/$repo"
            Write-Host "  ✓ Added AWS_ACCESS_KEY_ID" -ForegroundColor Green
        }
        
        # AWS_SECRET_ACCESS_KEY
        Write-Host "AWS_SECRET_ACCESS_KEY: " -NoNewline -ForegroundColor Cyan
        $awsSecret = Read-Host -AsSecureString
        if ($awsSecret.Length -gt 0) {
            $awsSecretPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($awsSecret))
            gh secret set AWS_SECRET_ACCESS_KEY --body $awsSecretPlain --repo "$owner/$repo"
            Write-Host "  ✓ Added AWS_SECRET_ACCESS_KEY" -ForegroundColor Green
        }
        
        # S3_PORTFOLIO_BUCKET
        Write-Host "S3_PORTFOLIO_BUCKET [vittcott-uploads-xyz123]: " -NoNewline -ForegroundColor Cyan
        $bucket = Read-Host
        if ([string]::IsNullOrWhiteSpace($bucket)) {
            $bucket = "vittcott-uploads-xyz123"
        }
        gh secret set S3_PORTFOLIO_BUCKET --body $bucket --repo "$owner/$repo"
        Write-Host "  ✓ Added S3_PORTFOLIO_BUCKET" -ForegroundColor Green
        
        Write-Host "`n✅ Secrets added successfully!`n" -ForegroundColor Green
    }
} else {
    Write-Host "❌ GitHub CLI not installed. You have 2 options:`n" -ForegroundColor Yellow
    
    Write-Host "OPTION 1: Install GitHub CLI (Recommended)" -ForegroundColor Cyan
    Write-Host "  Run: winget install --id GitHub.cli" -ForegroundColor White
    Write-Host "  Then run this script again`n" -ForegroundColor Gray
    
    Write-Host "OPTION 2: Add secrets manually (Easy)" -ForegroundColor Cyan
    Write-Host "  1. Go to: $secretsUrl" -ForegroundColor White
    Write-Host "  2. Click 'New repository secret'" -ForegroundColor White
    Write-Host "  3. Add each secret:" -ForegroundColor White
    Write-Host "     • GEMINI_API_KEY" -ForegroundColor Gray
    Write-Host "     • FINANCEHUB_API_KEY" -ForegroundColor Gray
    Write-Host "     • AWS_ACCESS_KEY_ID" -ForegroundColor Gray
    Write-Host "     • AWS_SECRET_ACCESS_KEY" -ForegroundColor Gray
    Write-Host "     • S3_PORTFOLIO_BUCKET = vittcott-uploads-xyz123`n" -ForegroundColor Gray
    
    Write-Host "Opening GitHub secrets page in browser..." -ForegroundColor Yellow
    Start-Process $secretsUrl
}

Write-Host "`n📖 Where to find your API keys:" -ForegroundColor Cyan
Write-Host "  • GEMINI_API_KEY: https://makersuite.google.com/app/apikey" -ForegroundColor Gray
Write-Host "  • FINANCEHUB_API_KEY: https://finnhub.io/dashboard" -ForegroundColor Gray
Write-Host "  • AWS keys: https://console.aws.amazon.com/iam/ → Users → Security credentials`n" -ForegroundColor Gray
