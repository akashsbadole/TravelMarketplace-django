# Tailwind CSS Build Guide

This guide explains how to build Tailwind CSS for the Travel Marketplace Django application.

## Prerequisites

Make sure you have Node.js and npm installed on your system. You can check by running:
```bash
node --version
npm --version
```

## Initial Setup

1. Install the Node.js dependencies:
   ```bash
   npm install
   ```

2. Build the CSS for the first time:
   ```bash
   python manage.py build_css
   ```

## Development Mode

For development with live reloading of CSS changes:

```bash
python manage.py build_css --watch
```

This will watch for changes in your CSS files and HTML templates and automatically rebuild the CSS.

## Production Build

For production deployment, build a minified version:

```bash
python manage.py build_css --minify
```

## File Structure

- `static/css/input.css` - The source Tailwind CSS file with custom components
- `static/css/output.css` - The generated CSS file (this is what gets loaded in the browser)
- `tailwind.config.js` - Tailwind configuration file
- `package.json` - Node.js dependencies and scripts

## How It Works

1. The Django management command `build_css` handles the CSS compilation process
2. It automatically installs npm dependencies if `node_modules` doesn't exist
3. The command runs `npx tailwindcss` with appropriate arguments based on the flags provided
4. The generated `output.css` file is then served by Django's static files system

## Making Changes

When you make changes to:
- HTML templates (Tailwind classes)
- The `input.css` file (custom styles)

The CSS will be automatically rebuilt if you're using watch mode, or you can manually rebuild by running the appropriate command.

## Troubleshooting

### "npx command not found"
- Make sure Node.js and npm are installed
- Ensure they are in your system's PATH

### CSS not updating
- Check that the `output.css` file exists in `static/css/`
- Verify you're running the Django server with static files serving enabled
- In production, make sure you've run `python manage.py collectstatic`

### Performance issues
- Use `--minify` flag for production builds
- Consider running CSS build as part of your deployment process

## Deployment

For production deployments, add the CSS build step to your deployment script:

```bash
# Install dependencies
npm install

# Build production CSS
python manage.py build_css --minify

# Collect static files
python manage.py collectstatic --noinput
```

## Notes

- The CDN version of Tailwind CSS has been removed from `templates/base.html`
- All custom styles have been moved to `static/css/input.css` within the `@layer components` directive
- The application now uses a locally compiled CSS file which resolves the production warning about using CDN