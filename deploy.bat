@echo off
echo ========================================
echo AUTO-DEPLOY TO RENDER.COM
echo ========================================
echo.

REM Check if GitHub CLI is installed
where gh >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo GitHub CLI not found. Let's use the web method instead.
    echo.
    echo STEP 1: Create GitHub Repository
    echo --------------------------------
    echo Opening GitHub in your browser...
    start https://github.com/new?name=unilag-scholar-metrics^&description=University+of+Lagos+Scholar+Metrics+Portal
    echo.
    echo Please:
    echo 1. Make it PUBLIC
    echo 2. Click "Create repository"
    echo 3. Copy the repository URL
    echo.
    pause
    
    echo.
    echo STEP 2: Push Your Code
    echo ----------------------
    set /p repo_url="Paste your repository URL here: "
    
    git remote add origin %repo_url% 2>nul
    git branch -M main
    git push -u origin main
    
    if %ERRORLEVEL% EQU 0 (
        echo ✓ Code pushed successfully!
        echo.
        echo STEP 3: Deploy on Render
        echo ------------------------
        echo Opening Render.com in your browser...
        start https://dashboard.render.com/
        echo.
        echo Please:
        echo 1. Sign up or log in
        echo 2. Click "New +" then "Web Service"
        echo 3. Connect your GitHub account
        echo 4. Select "unilag-scholar-metrics" repository
        echo 5. Use these settings:
        echo    - Name: unilag-scholar-metrics
        echo    - Environment: Python 3
        echo    - Build Command: pip install -r requirements.txt
        echo    - Start Command: gunicorn Crawlee:app
        echo    - Instance Type: Free
        echo 6. Click "Create Web Service"
        echo.
        echo Your app will be live in 2-3 minutes!
        echo.
        pause
    ) else (
        echo ✗ Failed to push. Make sure you entered the correct URL.
        echo.
        echo Try again with format: https://github.com/username/repo.git
        pause
    )
    
    goto :end
)

REM If GitHub CLI is available
echo GitHub CLI found! Using automated method...
echo.
echo STEP 1: Creating GitHub Repository
echo -----------------------------------
gh repo create unilag-scholar-metrics --public --source=. --remote=origin --push

if %ERRORLEVEL% EQU 0 (
    echo ✓ Repository created and code pushed!
    echo.
    echo STEP 2: Deploy on Render
    echo ------------------------
    echo Opening Render.com...
    start https://dashboard.render.com/
    echo.
    echo Please:
    echo 1. Click "New +" then "Web Service"
    echo 2. Select "unilag-scholar-metrics" repository
    echo 3. Use these settings:
    echo    - Build Command: pip install -r requirements.txt
    echo    - Start Command: gunicorn Crawlee:app
    echo    - Instance Type: Free
    echo 4. Click "Create Web Service"
    echo.
    pause
) else (
    echo ✗ GitHub CLI authentication needed
    echo Run: gh auth login
    echo Then run this script again
    pause
)

:end
echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Your app will be available at:
echo https://unilag-scholar-metrics.onrender.com
echo.
echo Check the Render dashboard for build status.
echo.
pause
