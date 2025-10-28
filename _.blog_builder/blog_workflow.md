# Blog Post Workflow

This document describes the workflow for creating blog posts from Jupyter notebooks.

## Overview

The `convert_notebook_to_blog.py` script converts Jupyter notebooks (exported to HTML via nbconvert) into styled blog posts that match the website's design.

## Prerequisites

Install the required dependencies:

```bash
pip install -r requirements-blog.txt
```

## Workflow

### Step 1: Create Your Blog Post as a Jupyter Notebook

Write your blog post in a Jupyter notebook (`.ipynb` file). Use:
- **Markdown cells** for text content, headings, lists, etc.
- **Code cells** for Python code and outputs
- **Images and plots** will be automatically included

### Step 2: Convert Notebook to HTML

Use nbconvert to convert your notebook to HTML:

```bash
jupyter nbconvert --to html your_notebook.ipynb
```

This will create `your_notebook.html` in the same directory.

### Step 3: Apply Blog Styling

Run the conversion script with your blog post metadata:

```bash
python convert_notebook_to_blog.py your_notebook.html \
    --title "Your Blog Post Title" \
    --date "Month Day, Year" \
    --description "A brief description of your blog post for SEO and social media" \
    --tags "Tag1,Tag2,Tag3" \
    --output blog/posts/your-post-slug.html
```

### Parameters

- `input`: Path to the nbconvert HTML file (required)
- `--title`: Title of your blog post (required)
- `--date`: Publication date in format "Month Day, Year" (required)
- `--description`: Brief description for SEO/social media (required)
- `--tags`: Comma-separated list of tags (required)
- `--keywords`: Optional SEO keywords (defaults to tags if not provided)
- `--output`: Output path for the final blog post (required)

### Example

```bash
# Convert notebook
jupyter nbconvert --to html card_game_analysis_blog.ipynb

# Apply blog styling
python convert_notebook_to_blog.py card_game_analysis_blog.html \
    --title "The APS 120 Card Game" \
    --date "January 28, 2025" \
    --description "Analyzing a solitaire-like card game from A Problem Squared podcast using Monte Carlo simulations." \
    --tags "Statistics,Python,Monte Carlo" \
    --output blog/posts/card-game-analysis.html
```

### Step 4: Update Blog Index

After creating your blog post, update `blog/index.html` to add a link to your new post in the blog listing.

## What the Script Does

1. Extracts notebook cells from the nbconvert HTML output
2. Converts markdown cells to clean HTML (removes Jupyter CSS classes and anchor links)
3. Styles code cells with the blog's code formatting
4. Preserves code outputs and images
5. Wraps everything in the blog template with:
   - Navigation header
   - Blog post metadata (title, date, tags)
   - Footer with social links
   - SEO meta tags

## Notes

- The script automatically handles:
  - Code syntax highlighting
  - Code outputs (text and images)
  - Markdown formatting
  - Internal links

- Images embedded in notebook outputs will be included automatically
- The output HTML file will have all necessary CSS and structure to match your existing blog posts

## Troubleshooting

If you encounter issues:

1. **BeautifulSoup4 not found**: Run `pip install beautifulsoup4`
2. **nbconvert not found**: Run `pip install nbconvert jupyter`
3. **Images not showing**: Check that image paths are correct relative to the output HTML location
