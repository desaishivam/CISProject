# Simple Django Website Guide

This is a basic guide to help you run and edit your Django website.

## Starting the Website

1. Open Terminal on your Mac:
   - Click on Spotlight (magnifying glass icon in top right)
   - Type "Terminal"
   - Click on Terminal app

2. Navigate to your website folder:
   ```
   cd /Users/shivam/Code/CISProject
   ```

3. Start the website:

python3 manage.py runserver
   ```
   
   ```

4. View your website:
   - Open any web browser (Safari, Chrome, etc.)
   - Go to: http://127.0.0.1:8000
   - You should see your website!

## Making Changes

### To edit the homepage text:
1. Open the file: `home/templates/home/index.html`
2. Edit the text between `<body>` and `</body>` tags
3. Save the file
4. Refresh your web browser to see the changes

### Important Notes:
- If you shut down your computer, the website will stop running
- To start it again, just follow the "Starting the Website" steps above
- You don't need to restart the website when you make changes to HTML files - just refresh your browser
- If the Terminal shows any error messages in red, make sure you're in the correct folder (step 2 above)

## Common Issues

1. If you see "command not found: python3":
   - You might need to install Python. Visit python.org to download it.

2. If the website doesn't start:
   - Make sure you're in the right folder (step 2 above)
   - Try closing Terminal and starting over

3. If changes don't appear:
   - Make sure you saved the file
   - Try refreshing your browser
   - If still not working, restart the website (stop it with Ctrl+C in Terminal, then run step 3 again)

## Need Help?
If you run into problems, try these steps in order:
1. Close everything and start over from step 1
2. Make sure you saved all your files
3. Make sure you're looking at http://127.0.0.1:8000 in your browser

Remember: Every time you restart your computer or close Terminal, you'll need to start the website again using these instructions. 