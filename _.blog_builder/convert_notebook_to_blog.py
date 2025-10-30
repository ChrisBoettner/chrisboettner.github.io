#!/usr/bin/env python3
"""
Convert Jupyter notebook HTML (from nbconvert) to blog-styled HTML.

Usage:
    python convert_notebook_to_blog.py input.html \
        --title "Blog Post Title" \
        --date "January 28, 2025" \
        --description "Blog post description" \
        --tags "Python,Data Science,ML" \
        --output blog/posts/output.html
"""

import argparse
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime


def extract_notebook_content(html_path):
    """Extract notebook cells from nbconvert HTML output."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Find the main content area with notebook cells
    main_content = soup.find('main')
    if not main_content:
        main_content = soup.find('body')

    cells = main_content.find_all('div', class_=re.compile(r'jp-Cell'))

    return cells


def convert_cell_to_blog_html(cell):
    """Convert a Jupyter notebook cell to blog HTML."""
    cell_html = []

    # Check if it's a markdown cell
    if 'jp-MarkdownCell' in cell.get('class', []):
        # Extract the rendered markdown content
        rendered = cell.find('div', class_='jp-MarkdownOutput')
        if rendered:
            # Get all the content and clean it up
            content = str(rendered)
            # Remove the wrapper div but keep the inner content
            content = re.sub(r'<div class="jp-MarkdownOutput[^"]*"[^>]*>', '', content)
            content = re.sub(r'<div class="jp-RenderedHTMLCommon[^"]*"[^>]*>', '', content)
            content = re.sub(r'<div class="jp-RenderedMarkdown[^"]*"[^>]*>', '', content)
            content = re.sub(r'</div>$', '', content.strip())
            # Remove Jupyter anchor links
            content = re.sub(r'<a class="anchor-link" href="[^"]*">¶</a>', '', content)
            # Remove data-mime-type attributes
            content = re.sub(r' data-mime-type="[^"]*"', '', content)
            # Clean up multiple closing divs that might be left
            content = re.sub(r'</div>\s*$', '', content.strip())
            cell_html.append(content)

    # Check if it's a code cell
    elif 'jp-CodeCell' in cell.get('class', []):
        # Extract code input
        input_area = cell.find('div', class_='jp-InputArea')
        if input_area:
            code = input_area.find('pre')
            if code:
                # Clean up the code
                code_text = code.get_text()
                cell_html.append(f'<div class="code-cell">\n    <pre>{code_text}</pre>\n</div>')

        # Extract code output (if any)
        output_area = cell.find('div', class_='jp-OutputArea')
        if output_area:
            # Look for text output
            text_outputs = output_area.find_all('pre')
            for output in text_outputs:
                output_text = output.get_text()
                if output_text.strip():
                    cell_html.append(f'<div class="code-output">\n    <pre>{output_text}</pre>\n</div>')

            # Look for HTML outputs (like animations)
            html_outputs = output_area.find_all('div', class_=re.compile(r'jp-RenderedHTMLCommon|output_html'))
            for html_output in html_outputs:
                # Get the HTML content, preserving all nested elements and scripts
                html_content = str(html_output)
                # Remove the outer wrapper div but keep all inner content
                html_content = re.sub(r'^<div[^>]*>', '', html_content)
                html_content = re.sub(r'</div>$', '', html_content.strip())
                if html_content.strip():
                    cell_html.append(f'<div class="code-output-html">\n{html_content}\n</div>')

            # Look for images
            images = output_area.find_all('img')
            for img in images:
                src = img.get('src', '')
                alt = img.get('alt', '')
                cell_html.append(f'<div class="code-output-image">\n    <img src="{src}" alt="{alt}" style="max-width: 100%; height: auto;">\n</div>')

    return '\n\n'.join(cell_html)


def create_blog_html(cells, title, date, description, tags, keywords=None):
    """Create complete blog HTML with styling and metadata."""

    # Convert cells to HTML
    content_parts = []
    has_notebook_title = False

    for i, cell in enumerate(cells):
        cell_html = convert_cell_to_blog_html(cell)
        if cell_html:
            # Check if first cell contains an h1 title - remove just the h1, keep other content
            if i == 0 and '<h1' in cell_html:
                has_notebook_title = True
                # Remove the h1 tag but preserve any content after it
                cell_html = re.sub(r'<h1[^>]*>.*?</h1>', '', cell_html, count=1, flags=re.DOTALL)
                cell_html = cell_html.strip()
            if cell_html:  # Only append if there's still content after removing h1
                content_parts.append(cell_html)

    content = '\n\n'.join(content_parts)

    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(',')]
    tags_html = ', '.join(f'<span class="tag">{tag}</span>' for tag in tag_list)

    # Use tags as keywords if keywords not provided
    if keywords is None:
        keywords = ', '.join(tag_list)

    # Create slug from title
    slug = title.lower().replace(' ', '-').replace(':', '').replace('|', '')
    slug = re.sub(r'[^a-z0-9-]', '', slug)

    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Chris Boettner</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">

    <!-- Open Graph / Social Media Meta Tags -->
    <meta property="og:title" content="{title} | Chris Boettner">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://chrisboettner.github.io/blog/posts/{slug}.html">

    <!-- Twitter Card data -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title} | Chris Boettner">
    <meta name="twitter:description" content="{description}">

    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22256%22 height=%22256%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 rx=%2220%22 fill=%22%23121212%22></rect><path fill=%22%23fff%22 d=%22M30.92 71.12L30.92 29.12Q34.08 28.36 38.74 27.64Q43.40 26.92 49.36 26.92Q55.52 26.92 59.76 28.44Q64.00 29.96 66.40 32.88Q68.80 35.80 68.80 40.16Q68.80 44.12 66.32 46.96Q63.84 49.80 59.84 51.24Q64.84 52.44 67.68 55.52Q70.52 58.60 70.52 63.84Q70.52 68.44 68.06 71.60Q65.60 74.76 60.96 76.40Q56.32 78.04 49.96 78.04Q43.96 78.04 38.80 77.40Q33.64 76.76 30.92 76.12L30.92 71.12ZM39.00 49.16L48.76 49.16Q54.32 49.16 57.12 47.08Q59.92 45.00 59.92 40.88Q59.92 38.32 58.68 36.64Q57.44 34.96 55.00 34.12Q52.56 33.28 48.76 33.28Q46.36 33.28 44.08 33.52Q41.80 33.76 39.96 34.12L39.00 34.36L39.00 49.16ZM39.00 71.12Q41.08 71.48 43.64 71.72Q46.20 71.96 49.24 71.96Q55.12 71.96 58.56 69.92Q62.00 67.88 62.00 63.28Q62.00 58.72 58.48 56.52Q54.96 54.32 48.76 54.32L39.00 54.32L39.00 71.12Z%22></path></svg>">
    <link rel="stylesheet" href="../../styles/main.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,700;1,400&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code&display=swap" rel="stylesheet">

    <!-- MathJax for LaTeX rendering -->
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$']],
                displayMath: [['$$', '$$']],
                processEscapes: true,
                processEnvironments: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
            }}
        }};
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

    <style>
        .code-cell {{
            background: #907552;
            border-radius: 8px;
            padding: 16px;
            margin: 20px 0;
            overflow-x: auto;
        }}
        .code-cell pre {{
            margin: 0;
            color: #e0e0e0;
            font-family: 'Fira Code', monospace;
            font-size: 14px;
            line-height: 1.5;
        }}
        .code-output {{
            background: #f5f5f5;
            border-left: 4px solid #4a9eff;
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
            font-size: 14px;
        }}
        .code-output pre {{
            margin: 0;
            color: #333;
        }}
        .code-output-image {{
            margin: 20px 0;
            text-align: center;
        }}
        .code-output-html {{
            margin: 20px 0;
            padding: 16px;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .code-output-html > div {{
            width: 100%;
            max-width: 100%;
        }}
        .cell-label {{
            font-size: 12px;
            color: #888;
            margin-bottom: 8px;
            font-family: 'Fira Code', monospace;
        }}
    </style>
</head>
<body>
    <nav>
        <a href="/" class="logo">CB.</a>
        <div class="nav-links">
            <a href="../../about.html">about</a>
            <a href="../../blog/index.html">blog</a>
            <a href="https://github.com/ChrisBoettner" target="_blank" aria-label="GitHub Profile">
                <svg height="24" width="24" viewBox="0 0 16 16" fill="black">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            </a>
            <a href="mailto:boettnec@gmail.com" aria-label="Email Me">
                <svg height="24" width="24" viewBox="0 0 24 24" fill="black">
                    <path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6zm-2 0l-8 5-8-5h16zm0 12H4V8l8 5 8-5v10z"/>
                </svg>
            </a>
        </div>
    </nav>

    <main>
        <article>
            <div class="blog-post-header">
                <h1>{title}</h1>
                <div class="meta">
                    <span>{date}</span>
                    <div class="tags">
                        {tags_html}
                    </div>
                </div>
            </div>

            <div class="blog-post-content">
                {content}
            </div>
        </article>
    </main>

    <footer>
        <div class="social-links">
            <a href="https://github.com/ChrisBoettner" target="_blank" aria-label="GitHub Profile">
                <svg height="24" width="24" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            </a>
            <a href="mailto:boettnec@gmail.com" aria-label="Email Me">
                <svg height="24" width="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6zm-2 0l-8 5-8-5h16zm0 12H4V8l8 5 8-5v10z"/>
                </svg>
            </a>
            <a href="https://www.linkedin.com/in/christopher-boettner-87aa21243/" target="_blank" aria-label="LinkedIn Profile">
                <svg height="24" width="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
            </a>
        </div>
        <p>&copy; {datetime.now().year} Chris Boettner. All rights reserved.</p>
    </footer>

    <script src="../../scripts/main.js"></script>
</body>
</html>
"""
    return template


def main():
    parser = argparse.ArgumentParser(
        description='Convert Jupyter notebook HTML to blog-styled HTML'
    )
    parser.add_argument('input', help='Input HTML file (from nbconvert)')
    parser.add_argument('--title', required=True, help='Blog post title')
    parser.add_argument('--date', required=True, help='Publication date (e.g., "January 28, 2025")')
    parser.add_argument('--description', required=True, help='Blog post description')
    parser.add_argument('--tags', required=True, help='Comma-separated tags (e.g., "Python,Data Science")')
    parser.add_argument('--keywords', help='SEO keywords (defaults to tags)')
    parser.add_argument('--output', required=True, help='Output HTML file path')

    args = parser.parse_args()

    # Extract notebook content
    print(f"Reading notebook from {args.input}...")
    cells = extract_notebook_content(args.input)
    print(f"Found {len(cells)} cells")

    # Create blog HTML
    print("Converting to blog format...")
    blog_html = create_blog_html(
        cells=cells,
        title=args.title,
        date=args.date,
        description=args.description,
        tags=args.tags,
        keywords=args.keywords
    )

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(blog_html)

    print(f"Blog post created at {output_path}")
    print(f"\nTo use this script in the future:")
    print(f"1. Convert notebook to HTML: jupyter nbconvert --to html your_notebook.ipynb")
    print(f"2. Run this script with your metadata:")
    print(f'   python convert_notebook_to_blog.py your_notebook.html \\')
    print(f'       --title "Your Title" \\')
    print(f'       --date "Month Day, Year" \\')
    print(f'       --description "Your description" \\')
    print(f'       --tags "Tag1,Tag2,Tag3" \\')
    print(f'       --output blog/posts/your-post.html')


if __name__ == '__main__':
    main()
