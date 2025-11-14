from django.core.management.base import BaseCommand
import os
import subprocess
import sys
from pathlib import Path


class Command(BaseCommand):
    help = 'Build Tailwind CSS for production or development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Run in watch mode for development',
        )
        parser.add_argument(
            '--minify',
            action='store_true',
            help='Minify CSS for production',
        )

    def handle(self, *args, **options):
        # Get project base directory
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        
        # Check if node_modules exists, if not run npm install
        node_modules_path = base_dir / 'node_modules'
        if not node_modules_path.exists():
            self.stdout.write('Installing Node.js dependencies...')
            try:
                subprocess.run(['npm', 'install'], cwd=base_dir, check=True)
                self.stdout.write(self.style.SUCCESS('Dependencies installed successfully'))
            except subprocess.CalledProcessError:
                self.stdout.write(self.style.ERROR('Failed to install dependencies. Make sure Node.js and npm are installed.'))
                return

        # Build command
        if options['watch']:
            cmd = ['npx', 'tailwindcss', '-i', './static/css/input.css', '-o', './static/css/output.css', '--watch']
            self.stdout.write('Starting Tailwind CSS in watch mode...')
        elif options['minify']:
            cmd = ['npx', 'tailwindcss', '-i', './static/css/input.css', '-o', './static/css/output.css', '--minify']
            self.stdout.write('Building minified CSS for production...')
        else:
            cmd = ['npx', 'tailwindcss', '-i', './static/css/input.css', '-o', './static/css/output.css']
            self.stdout.write('Building CSS for development...')

        try:
            if options['watch']:
                # For watch mode, we need to run the command directly
                subprocess.run(cmd, cwd=base_dir)
            else:
                # For regular build, capture output
                result = subprocess.run(cmd, cwd=base_dir, check=True, capture_output=True, text=True)
                if result.stdout:
                    self.stdout.write(result.stdout)
                self.stdout.write(self.style.SUCCESS('CSS built successfully'))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Failed to build CSS: {e}'))
            if e.stdout:
                self.stdout.write(f'Stdout: {e.stdout}')
            if e.stderr:
                self.stdout.write(f'Stderr: {e.stderr}')
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('npx command not found. Make sure Node.js and npm are installed and in your PATH.'))